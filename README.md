# pulumi-python-acls

An Infrastructure as Code example managing [Tailscale](https://tailscale.com) network access control lists (ACLs) using [Pulumi](https://www.pulumi.com) and Python.

## Example ACL output

As an example this ACL file:

```json
{
	"acls": [
		{
			"action": "accept",
			"src": [
				"autogroup:admin"
			],
			"dst": [
				"tag:saas:443"
			]
		},
		{
			"action": "accept",
			"src": [
				"group:support"
			],
			"dst": [
				"10.0.100.0/24:443"
			]
		},
		{
			"action": "accept",
			"src": [
				"group:support"
			],
			"dst": [
				"10.0.101.0/24:443"
			]
		},
		{
			"action": "accept",
			"src": [
				"group:support"
			],
			"dst": [
				"10.0.102.0/24:443"
			]
		}
	],
	"autoApprovers": {
		"routes": {
			"10.0.0.0/24": [
				"tag:saas"
			],
			"10.0.100.0/24": [
				"tag:customer-customer1"
			],
			"10.0.101.0/24": [
				"tag:customer-customer2"
			],
			"10.0.102.0/24": [
				"tag:customer-customer3"
			]
		}
	},
	"groups": {
		"group:support": [
			"cameron@example.com"
		]
	},
	"tagOwners": {
		"tag:customer-customer1": [
			"tag:customer-deployer"
		],
		"tag:customer-customer2": [
			"tag:customer-deployer"
		],
		"tag:customer-customer3": [
			"tag:customer-deployer"
		],
		"tag:customer-deployer": [
			"tag:deployer"
		],
		"tag:deployer": [],
		"tag:saas": [
			"tag:deployer"
		]
	}
}
```

was generated based on this `customer_csv` data:

```
customer_csv = """
customer1,10.0.100.0/24
customer2,10.0.101.0/24
customer3,10.0.102.0/24
"""
```

and this jinja2 template:

```
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
```
