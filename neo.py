# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
  lookup: neo
  author: Kees de Jong (kees.dejong+dev@neo****.nl)
  version_added: "0.1"
  short_description: Extract a specific value from lists/dicts
  description:
    - Filter out specific data from lists and return a selected value
  options:
    _terms:
      description: Data provided for lookup, filter value, selector value
      required: True
    select_key:
      description: Override the default 'name' filter key
      required: False
  notes:
    - By default the lookup plugin takes in 'name' as selector (selectattr),
      this can be changed by providing using the selector flag as
      fourth argument.
"""

EXAMPLES = """
vars:
  people:
    - name: jdoe
      role: admin
    - name: ajones
      role: crackpot
    - name: jpicard
      role: captain

# below are filters chained to return a value, the same is done by the task below it
# "{{ people | selectattr('name', '==', 'jdoe') | map(attribute='role') | first }}"
- name: return role value from person called jdoe
  debug: msg="{{ lookup('neo', people, 'jdoe', 'role') }}"

# below are filters chained to return a value, the same is done by the task below it
# "{{ people | selectattr('role', '==', 'admin') | map(attribute='name') | first }}"
- name: return the name of people with the admin role
  debug: msg="{{ lookup('neo', people, 'admin', 'name', {'select_key': 'role'}) }}"
"""

RETURN = """
  _string:
    description:
      - Return selected value from filtered data
"""

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
from ansible.utils.listify import listify_lookup_plugin_terms
from ansible.module_utils.six import string_types


display = Display()
FLAGS = ('select_key',)

class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):

        def _raise_terms_error(msg=""):
            raise AnsibleError(
                "neo lookup expects: data (list of dicts), select value, filter value, [{'select_key': 'selector'}, where selector is by default 'name']. " + msg)

        terms[0] = listify_lookup_plugin_terms(terms[0], templar=self._templar, loader=self._loader)

        # check lookup terms - check number of terms
        if not isinstance(terms, list) or not 3 <= len(terms) <= 4:
            _raise_terms_error()

        items = terms[0] # data provided
        select_value = terms[1] # used to create subset selection of data (items)
        filter_value = terms[2] # used to return a value from the data subset

	# first term should be a list (or dict), second a string holding the select value, third a string holding a filter value
        if not isinstance(items, (list, dict)) or not isinstance(select_value, string_types) or not isinstance(filter_value, string_types):
            _raise_terms_error()

        flags = {}
        if len(terms) == 4:
            flags = terms[3]
            # optional fourth term should be a dict holding a filter key
            if not isinstance(flags, dict) and not all([isinstance(key, string_types) and key in FLAGS for key in flags]):
                _raise_terms_error("The optional fourth item must be a dict with flags '{}'.".format(FLAGS))

            # parsing flags
            if flags.get('select_key', False) and isinstance(flags['select_key'], string_types):
                select_key = flags['select_key']
                display.vvv("Filter key default 'name' overridden with '{}'.".format(select_key))
            else:
                display.vvv("Default filter key will be set to 'name'.")

        # running filter
        for item in items:
            if 'select_key' in locals() and item.get(select_key, False):
                selected_key = item[select_key]
            else:
                # if no (valid) filter key is provided, the default is set to 'name'
                selected_key = item['name']
            display.vvvv("Comparing '{}' with '{}'.".format(selected_key, select_value))

            # look for a match in the value lookup and continue in this subset of the data
            if selected_key == select_value:
                # filter out the value from the subset to return
                if filter_value in item:
                    display.vvv("Found filter match for '{}: {}' in data subset '{}: {}'.".format(
                        select_key if 'select_key' in locals() else 'name',
                        select_value, filter_value, item[filter_value]))
                    return [item[filter_value]]

        _raise_terms_error("Failed to find filter match for '{}: {}' in data subset '{}'.".format(
            select_key if 'select_key' in locals() else 'name',
            select_value, filter_value))
