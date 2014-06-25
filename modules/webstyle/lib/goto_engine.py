## This file is part of Invenio.
## Copyright (C) 2012 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
Redirecting engine.
"""

import os
import optparse

from invenio.config import CFG_PYLIBDIR
from invenio.dbquery import run_sql, IntegrityError
from invenio.jsonutils import json, json_unicode_to_utf8
from invenio.pluginutils import PluginContainer, get_callable_documentation
from invenio.textutils import wait_for_user

CFG_GOTO_PLUGINS = PluginContainer(os.path.join(CFG_PYLIBDIR, 'invenio',
'goto_plugins', 'goto_plugin_*.py'), plugin_builder=lambda name, code: code.goto)

def register_redirection(label, plugin, parameters=None, update_on_duplicate=False):
    """
    Register a redirection from /goto/<LABEL> to the URL returned by running the
    given plugin (as available in CFG_GOTO_PLUGINS), with the given parameters.

    @param label: the uniquely identifying label for this redirection
    @type label: string

    @param plugin: the algorithm that should resolve the redirection, usually:
        "goto_plugin_FOO"
    @type plugin: string

    @param parameters: further parameters that should be passed to the plugin.
        This should be a dictionary or None. Note that these parameters could
        be overridden by the query parameters.
    @type parameters: dict or None

    @param update_on_duplicate: if False (default), if the label already exist it
        L{register_redirection} will raise a ValueError exception. If True, it
        will implicitly call L{update_redirection}.
    @type update_on_duplicate: bool

    @raises: ValueError in case of duplicate label and L{update_on_duplicate} is
        set to False.

    @note: parameters are going to be serialized to JSON before being stored
        in the DB. Hence only JSON-serializable values should be put there.
    """
    if run_sql("SELECT label FROM goto WHERE label=%s", (label, )):
        raise ValueError("%s label already exists" % label)
    if plugin not in CFG_GOTO_PLUGINS:
        raise ValueError("%s plugin does not exist" % plugin)
    if parameters is None:
        parameters = {}
    try:
        parameters.items() ## dummy test to see if it exposes the dict interface
        json_parameters = json.dumps(parameters)
    except Exception, err:
        raise ValueError("The parameters %s do not specify a valid JSON map: %s" % (parameters, err))
    try:
        run_sql("INSERT INTO goto(label, plugin, parameters, creation_date, modification_date) VALUES(%s, %s, %s, NOW(), NOW())", (label, plugin, json_parameters))
    except IntegrityError:
        if run_sql("SELECT label FROM goto WHERE label=%s", (label,)):
            if update_on_duplicate:
                update_redirection(label=label, plugin=plugin, parameters=parameters)
            else:
                raise ValueError("%s label already exists" % label)
        else:
            ## This is due to some other issue
            raise

def update_redirection(label, plugin, parameters=None):
    """
    Update an existing redirection from /goto/<LABEL> to the URL returned by
    running the given plugin (as available in CFG_GOTO_PLUGINS), with the given
    parameters.

    @param label: the uniquely identifying label for this redirection
    @type label: string

    @param plugin: the algorithm that should resolve the redirection, usually:
        "goto_plugin_FOO"
    @type plugin: string

    @param parameters: further parameters that should be passed to the plugin.
        This should be a dictionary or None. Note that these parameters could
        be overridden by the query parameters.
    @type parameters: dict or None

    @raises: ValueError in case the label does not already exist.

    @note: parameters are going to be serialized to JSON before being stored
        in the DB. Hence only JSON-serializable values should be put there.
    """
    if not run_sql("SELECT label FROM goto WHERE label=%s", (label, )):
        raise ValueError("%s label does not already exist" % label)
    if plugin not in CFG_GOTO_PLUGINS:
        raise ValueError("%s plugin does not exist" % plugin)
    if parameters is None:
        parameters = {}
    try:
        parameters.items() ## dummy test to see if it exposes the dict interface
        json_parameters = json.dumps(parameters)
    except Exception, err:
        raise ValueError("The parameters %s do not specify a valid JSON map: %s" % (parameters, err))
    run_sql("UPDATE goto SET plugin=%s, parameters=%s, modification_date=NOW() WHERE label=%s", (plugin, json_parameters, label))

def drop_redirection(label):
    """
    Delete an existing redirection identified by label.

    @param label: the uniquely identifying label for this redirection
    @type label: string
    """
    run_sql("DELETE FROM goto WHERE label=%s", (label, ))

def get_redirection_data(label):
    """
    Returns all information about a given redirection identified by label.

    @param label: the label identifying the redirection
    @type label: string

    @returns: a dictionary with the following keys:
        * label: the label
        * plugin: the name of the plugin
        * parameters: the parameters that are passed to the plugin
            (deserialized from JSON)
        * creation_date: datetime object on when the redirection was first
            created.
        * modification_date: datetime object on when the redirection was
            last modified.
    @rtype: dict

    @raises ValueError: in case the label does not exist.
    """
    res = run_sql("SELECT label, plugin, parameters, creation_date, modification_date FROM goto WHERE label=%s", (label, ))
    if res:
        return {'label': res[0][0],
                 'plugin': CFG_GOTO_PLUGINS[res[0][1]],
                 'parameters': json_unicode_to_utf8(json.loads(res[0][2])),
                 'creation_date': res[0][3],
                 'modification_date': res[0][4]}
    else:
        raise ValueError("%s label does not exist" % label)

def is_redirection_label_already_taken(label):
    """
    Returns True in case the given label is already taken.
    """
    return bool(run_sql("SELECT label FROM goto WHERE label=%s", (label,)))

def main():
    """
    Entry point for the CLI
    """
    def get_json_parameters_from_cli(dummy_option, dummy_opt_str, value, parser):
        try:
            setattr(parser.values, 'parameters', json_unicode_to_utf8(json.loads(value)))
        except Exception, err:
            raise optparse.OptionValueError("Cannot parse as a valid JSON serialization the provided parameters: %s. %s" % (value, err))

    def get_parameter_from_cli(dummy_option, dummy_opt_str, value, parser):
        if not hasattr(parser.values, 'parameters'):
            setattr(parser.values, 'parameters', {})
        param, value = value.split('=', 1)
        try:
            value = int(value)
        except:
            pass
        parameters = parser.values.parameters
        parameters[param] = value
        setattr(parser.values, 'parameters', parameters)

    parser = optparse.OptionParser()

    plugin_group = optparse.OptionGroup(parser, "Plugin Administration Options")
    plugin_group.add_option("--list-plugins", action="store_const", dest="action", const="list-goto-plugins", help="List available GOTO plugins and their documentation")
    plugin_group.add_option("--list-broken-plugins", action="store_const", dest="action", const="list-broken-goto-plugins", help="List broken GOTO plugins")
    parser.add_option_group(plugin_group)

    redirection_group = optparse.OptionGroup(parser, "Redirection Manipultation Options")
    redirection_group.add_option("-r", "--register-redirection", metavar="LABEL", action="store", dest="register", help="Register a redirection with the provided LABEL")
    redirection_group.add_option("-u", "--update-redirection", metavar="LABEL", action="store", dest="update", help="Update the redirection specified by the provided LABEL")
    redirection_group.add_option("-g", "--get-redirection", metavar="LABEL", action="store", dest="get_redirection", help="Get all information about a redirection specified by LABEL")
    redirection_group.add_option("-d", "--drop-redirection", metavar="LABEL", action="store", dest="drop_redirection", help="Drop an existing redirection specified by LABEL")
    parser.add_option_group(redirection_group)

    specific_group = optparse.OptionGroup(parser, "Specific Options")
    specific_group.add_option("-P", "--plugin", metavar="PLUGIN", action="store", dest="plugin", help="Specify the plugin to use when registering or updating a redirection")
    specific_group.add_option("-j", "--json-parameters", metavar="PARAMETERS", action="callback", type="string", callback=get_json_parameters_from_cli, help="Specify the parameters to provide to the plugin (serialized in JSON)")
    specific_group.add_option("-p", "--parameter", metavar="PARAM=VALUE", action="callback", callback=get_parameter_from_cli, help="Specify a single PARAM=VALUE parameter to be provided to the plugin (alternative to the JSON serialization)", type="string")
    parser.add_option_group(specific_group)

    (options, dummy_args) = parser.parse_args()
    if options.action == "list-goto-plugins":
        print "GOTO plugins found:"
        for component, goto in CFG_GOTO_PLUGINS.items():
            print component + ' -> ' + get_callable_documentation(goto)
    elif options.action == 'list-broken-goto-plugins':
        print "Broken GOTO plugins found:"
        for component, error in CFG_GOTO_PLUGINS.get_broken_plugins().items():
            print component + '->' + str(error)
    elif options.register:
        label = options.register
        plugin = options.plugin
        parameters = getattr(options, 'parameters', {})
        if not plugin in CFG_GOTO_PLUGINS:
            parser.error("%s is not a valid plugin" % plugin)
        if is_redirection_label_already_taken(label):
            parser.error("The specified label %s is already taken" % label)
        register_redirection(label, plugin, parameters)
        print "The redirection %s was successfully registered for the plugin %s with parameters %s" % (label, plugin, parameters)
    elif options.update:
        label = options.update
        if not is_redirection_label_already_taken(label):
            parser.error("The specified label %s does not exist" % label)
        redirection_data = get_redirection_data(label)
        plugin = options.plugin or redirection_data['plugin']
        parameters = options.parameters or redirection_data['parameters']
        if not plugin in CFG_GOTO_PLUGINS:
            parser.error("%s is not a valid plugin" % plugin)
        update_redirection(label, plugin, parameters=None)
        print "The redirection %s was successfully updated for the plugin %s with parameters %s" % (label, plugin, parameters)
    elif options.get_redirection:
        label = options.get_redirection
        if not is_redirection_label_already_taken(label):
            parser.error("The specified label %s does not exist" % label)
        print get_redirection_data(label)
    elif options.drop_redirection:
        label = options.drop_redirection
        if is_redirection_label_already_taken(label):
            wait_for_user("Are you sure you want to drop the redirection: %s\n%s" % (label, get_redirection_data(label)))
            drop_redirection(label)
            print "The redirection %s was successfully dropped" % label
        else:
            print "The specified label %s is not registered with any redirection" % label
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
