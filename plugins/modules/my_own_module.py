#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: my_own_module
short_description: Create/update a text file with given content
version_added: "1.0.0"
description:
  - Creates a text file at path with provided content.
  - Idempotent: changes only if content differs or file does not exist.
options:
  path:
    description: Absolute path to the file.
    required: true
    type: str
  content:
    description: Content to write.
    required: true
    type: str
author:
  - You
'''

EXAMPLES = r'''
- name: Create file
  my_own_module:
    path: /tmp/hello.txt
    content: "hello\n"
'''

RETURN = r'''
changed:
  description: Whether something changed.
  type: bool
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import os


def read_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_text(path, content):
    parent = os.path.dirname(path) or '.'
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def run_module():
    module_args = dict(
        path=dict(type='str', required=True),
        content=dict(type='str', required=True),
    )

    result = dict(changed=False)

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    path = module.params['path']
    content = module.params['content']

    # 1) если файла нет — будет создание
    if not os.path.exists(path):
        result['changed'] = True
        if module.check_mode:
            module.exit_json(**result)
        try:
            write_text(path, content)
        except Exception as e:
            module.fail_json(msg=f"Cannot create file: {e}", **result)
        module.exit_json(**result)

    # 2) если файл есть — сравниваем содержимое
    try:
        current = read_text(path)
    except Exception as e:
        module.fail_json(msg=f"Cannot read file: {e}", **result)

    if current != content:
        result['changed'] = True
        if module.check_mode:
            module.exit_json(**result)
        try:
            write_text(path, content)
        except Exception as e:
            module.fail_json(msg=f"Cannot update file: {e}", **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()