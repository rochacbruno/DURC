# DURC

<img src="./imgs/duct_mini.png">
<br>

A **framework** and **specification** for writing and running automated declarative cases for testing or reproducibility.

- **D**eclarative
- **U**nderstandable
- **R**eproducible
- **C**ases

## Why does DURC exists

Writing test cases is a task that requires at least the following skills:

- Knowledge of the **product/components** being exercised.
- Knowledge of automation **strategies**.
- Knowledge of the **programming language** used for automation.
- Knowledge of the **tools and frameworks**.
- Knowledge of how the **metrics** are being gathered and reported.
- Knowledge of how to prepare the **environment** to run the tests.
- Knowledge on how to report reproducible **bug reports**.

There is too much **Knowledge** one needs to master before starting 
creating automation.

**DURC** aims to make testing easier, not only easier, but maintainable, reproducible and understandable by removing the need
of some of knowledges above, so **Quality can be everyone's responsibility**, even the ones who are not testers/programmers.

Using our idiom, we want **DURC** testing.

- A **Declarative** (but strict) language for describing test scenarios.
- That can be **Understable** by humans reading it.
- And also **Reproducible** by automation engine (a.k.a: _Ansible_)

## Who is interested in DURC

- Developer
  - To write automation while developing a feature and save time of collaboration to QA/QE.
- CEE/Support
  - To reproduce customer cases, to report reproducible scenarios to Dev/QE
- QA/QE
  - To reuse cases written by Customer/Dev/CEE, to write collaboratively new test scenarios.
- Manager
  - To evaluate better the priority and value of cases that are Understandable.
- Customer
  - To reproduce steps provided by CEE.

## How it works

### Engine

**DURC** relies on the awesome **Ansible** so it follows the same principles, 
a **DURC** case is written in form of Ansible plays (that can be single playable yaml files or complete roles) with tasks using testing modules.

### Modules

**DURC** relies on existing Ansible [testing Strategies](https://docs.ansible.com/ansible/latest/reference_appendices/test_strategies.html) + a set of specialized tools to provide the best test automation experience.

Also it comes with wrappers for existing testing frameworks like py.test and  selenium.

### Semantic

As the name says, test scenarios must be **Declarative** in the same way the Ansible playbooks works, it must be described using YAML syntax and Ansible idioms and special syntax.

The test scenarios must be also **Understandable** by humans so one would be able to open the YAML file and read it as it is a step by step manual of how to reproduce that scenario manually if needed.

Also the yaml file should be **Reproducible** by automation, that means a person or an automation pipeline can use a pre defined container and just run against that declarative file with no issue.

Example of a **Case**:

`case_positive_login_with_user.yaml`

```yaml
---
- hosts: localhost
  gather_facts: no
  vars:
    urls:
      login_page: http://localhost:8000/login
  tasks:

    - name: Meta
      block: 
        - durc_metadata:
          id: 12345
          description: This case reproduces the user login workflow.
          level: Critical
          customerscenario: true
        - durc_skip:
            bugzilla_is_open: 456789

    - name: Arrange
      block:
        - name: Create a user `foo` on the web system
          durc_api:
            handler: myproduct.user.create  # custom handlers by product
            data: username=foo password=bar
            cleanup: created_user.delete
          register: created_user

    - name: Act
      block:
        - name: Navigate to Login page
          durc_ui:
            open: "{{ urls.login_page }}"
            wait_for: "{{ css('#login_form') }}"
          register: login_form

        - name: Fill the Login Form
          durc_ui:
            object: login_form
            fill:
              username: created_user.username
              password: created_user.password.uncrypted
            submit: true
          register: response

    - name: Assert
      block:
        - name: Login was successful
          assert:
            that: "'Logged in as user' in response.content"
```

Once **D**eclared and having the the product accessible on `http://localhost:8000` it should be easy to **U**understand and follow the steps ot to **R**eproduce the **Case** using:

```bash
$ pip install ansible-durc
$ durc reproduce case_positive_login_with_user.yaml

# or

$ dnf install docker
$ docker run durc/durc reproduce case_positive_login_with_user.yaml
```

#### PROS

- Readable by non programmers
- Writable by non programers
- Declarative
- Abstracted
- Strict (can be validated)
- Effortless environment (ansible-runner container image)

#### CONS

- Verbose - 48 lines of YAML

------

Now lets compare the same written in 52 lines of Python.

`test_positive_login_with_user.py`

```py
# coding: utf-8
"""Test module description"""
import unittest
import myproductlib

from selenium import webdriver
from some_module.decorators import skip_if, bug_is_open


driver = driver = webdriver.Chrome()

urls = {'login_page': 'http://localhost:8000/login'}


class UserLoginTestCase(unittest.TestCase):
    """This class tests user login."""

    def setUp(self):
        """Arrange step."""
        self.created_user = myproductlib.user.create(
            username='foo', password='bar'
        )

    def tearDown(self):
        """Arrange step teardown"""
        self.created_user.delete()

    @skip_if(bug_is_open("bugzilla", 456789))
    def test_positive_login_with_user(self):
        """This case reproduces the user login workflow.

        :id: 12345
        :level: Critical
        :customerscenario: true
        """
        # Act
        driver.get(urls['login_page'])

        username = driver.find_element_by_name("username")
        username.clear()
        username.send_keys(self.created_user.username)

        password = driver.find_element_by_name("password")
        password.clear()
        password.send_keys(self.created_user.password)

        driver.find_element_by_css("#login_form.input[type=submit]").click()

        # Assert
        self.assertIn("Logged in as user:", driver.get_attribute('inner_html'))

```

and then to run it:

```bash
$ dnf install chrome-driver
$ pip install pytest selenium
$ py.test -v test_positive_login_with_user.py --junit=report.xml --other --options
```

#### PROS

- Flexibility (for programmers only)

#### CONS

- Writable only by programmers
- Readable mostly only by programmers
- Python environment is sometimes tricky to setup
- Too much flexible (we can have linters for code style but not easy to check test correctness)
- Code is more difficult to maintain and review

### Metrics

**Ansible** can already generate **Junit** [files](https://docs.ansible.com/ansible/latest/plugins/callback/junit.html)

## FAQ

### Why not just write test scenarios in Python?

#### it doesn't fit

First, we are not talking only about **tests** we are referring to it as **cases** because sometimes it is more than tests, 
it can be reproducible solutions provided by CEE to Customer, By Dev to QE and also used to automate different kind of tasks in an RPA project.

The same case described above could be written in Python, but that does not meet the **DURC** requirements:

- **D**eclarative
  - Python tests are dependant of a programming flow and it is not trivial to make things idempotent and declarative.
- **U**nderstandable
  - Non programmers cannot easily understand the steps to reproduce that case, also to write the tests it is required to know the programmming language, the frameworks, the rules.
- **R**eproducible
  - To run single, isolated test cases written for example using Py.Test, one should prepare the whole environment which is not something one want to suggest a customer to do.
- **C**ases
  - As said, not only tests, but any kind of automation case.

#### Code has a cost

There is a cost on maintaining code, together with the testing flow it is also needed to maintain the whole framework and tooling, we want **less code** and more **case automation**.

Having a standard **framework** on top of a well known and robust engine (a.k.a _Ansible_) makes total sense.

The end cost of maintaining, reviewing and reproducing **declarative** scenarios has been proved a good idea by Ansible itself.

### Why not adopt an Uniquitous language like Gherkin?

#### Cost of maintainance

Gherkin is a descriptive language for **BDD** and it requires that the syntax matches with tokens defined inside the project specification, for example, to use a `having login page opened do:` working, one will need to write a handler for `having` and `opened` tokens. We want **DURC** to be prodcut/project agnostic.

#### Error prone

It is not easy to keep a Gherkin code strictly right, it is easy to commit a typo.


### Who will develop and maintain the `durc_` modules?

#### Does not matter!

**DURC** is more like an specification and base modules, it is open to anyone to inherit from `durc_` std library to customize its own modules as long it follows the DURC specifications and rules.

That means, for example, you have a product which delivers a REST api, you can use **durc_api** as base for your **durc_foo_api** and you can maintain it, host it etc. DURC will only need it to be discoverable under the Ansible virtual environment. (ex: `pip install durc_foo_api`).

However, **DURC** will do the best to deliver the base modules for most common tasks in case automation like talking to APIs, CLIs, SSH client, Authentication methods, Conditionals, Fixtures and Reporting.
