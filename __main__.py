"""A Python Pulumi program"""

from jinja2 import Template

from io import StringIO
import pandas as pd
import pulumi_tailscale as tailscale

#
# Use your customer data to define ACLs, routes, etc.
# You can move this to a separate CSV or query this from a database.
#
customer_csv = """
customer1,10.0.100.0/24
customer2,10.0.101.0/24
customer3,10.0.102.0/24
"""

#
# Customize this based on your ACL needs.
# Note the {% for c in customer_list %} ... {% endfor %} loops to iterate over your customer_csv data from above.
#
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
        "tag:customer-{{ c.customerName }}": ["tag:customer-deployer"],
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

#
# Parse the customer data
#
csvData = pd.read_csv(StringIO(customer_csv), header=None, names=['customerName', 'customerSubnet'])
data_dict = csvData.to_dict(orient='records')

#
# Render the template
#
template = Template(template_string)
rendered_json = template.render(customer_list=data_dict)
# print(rendered_json)

#
# Manage the ACL file via Pulumi
#
tailscale.Acl('acl',acl=rendered_json)
