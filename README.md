# Neo: Custom Ansible lookup plugin
I made this custom Ansible plugin to simplify variable lookups for my Ansible managed cloud cluster at home called Neobits.

## Examples
```
vars:
  people:
    - name: jdoe
      role: admin
    - name: ajones
      role: crackpot
    - name: jpicard
      role: captain
```

Below is a lookup chained to return a value, the same is done by the task below it, but then simplified with my plugin.

`"{{ people | selectattr('name', '==', 'jdoe') | map(attribute='role') | first }}"`

And now simplified with my plugin.
```
- name: return role value from person called jdoe
  debug: msg="{{ lookup('neo', people, 'jdoe', 'role') }}"
```

Below are filters again chained to return a value, and below that is another simplified method by using my plugin.

`"{{ people | selectattr('role', '==', 'admin') | map(attribute='name') | first }}"`

And now simplified with my plugin.
```
- name: return the name of people with the admin role
  debug: msg="{{ lookup('neo', people, 'admin', 'name', {'select_key': 'role'}) }}"
```

## Installation
Create a folder in the top level directory of your playbooks called [lookup_plugins](https://docs.ansible.com/ansible/latest/plugins/lookup.html#enabling-lookup-plugins), and place the plugin there. After that you are able to make use of it.
