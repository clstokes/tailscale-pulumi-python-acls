"""A Python Pulumi program"""

from jinja2 import Template

from io import StringIO
import pandas as pd
import pulumi_tailscale as tailscale

customer_csv = """
customer1,10.0.100.0/24
customer2,10.0.101.0/24
customer3,10.0.102.0/24
"""

template_string = """
{
    "groups": {
        "group:support": [
            "cameron@example.com",
        ],
    },
    "tagOwners": {
        "tag:deployer":          [], // Used by Pulumi
        "tag:saas":              ["tag:deployer"],
        "tag:customer-deployer": ["tag:deployer"],

        // customers
        {% for c in customer_list %}
        "tag:customer-{{ c.customerName }}": ["tag:customer-deployer"], // TODO: move tag:customers to a constant
        {% endfor %}
    },
    "autoApprovers": {
        "routes": {
            "10.0.0.0/24":  ["tag:saas"],

            // customers
            {% for c in customer_list %}
            "{{ c.customerSubnet }}": ["tag:customer-{{ c.customerName }}"],
            {% endfor %}
        },
    },
    "acls": [
        { // general access
            "action": "accept",
            "src": [
                "autogroup:admin",
            ],
            "dst": [
                "tag:saas:443",
            ],
        },
        // customers
        {% for c in customer_list %}
        { // {{ c.customerName }}
            "action": "accept",
            "src": [
                "group:support",
            ],
            "dst": [
                "{{ c.customerSubnet }}:443",
            ],
        },
        {% endfor %}
    ],
}
"""

csvData = pd.read_csv(StringIO(customer_csv), header=None, names=['customerName', 'customerSubnet'])
data_dict = csvData.to_dict(orient='records')

template = Template(template_string)
rendered_json = template.render(customer_list=data_dict)

# print(rendered_json)

tailscale.Acl('acl',acl=rendered_json)
