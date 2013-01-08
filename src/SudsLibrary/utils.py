# Copyright 2012 Kevin Ormbrek
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from robot.libraries.BuiltIn import BuiltIn


# assumed that no WSDL will have a service or port named "1", etc.
def parse_index(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return value


def to_bool(item):
    return BuiltIn().convert_to_boolean(item)
