# Work Sample
Project using Troposphere to generate a CloudFormation script.

# Design Considerations
The majority of the example scripts provided with the Troposphere library represent direct translations of a CloudFormation template without consideration for extensibility, efficiency, or future use by programmers not familiar with the library. The first iteration of my script looked very much like the examples, but then I started identifying areas of improvement:
## Paramaterization
Based on AWS Best Practice surrounding CloudFormation, I identified the following parameters to be added for extensibility:
* Environment
* Owner
* Service
* VPC

This will allow the generated template to be reused, removing the need to generate a new template when you need to deploy to testing and production environments. Additional parameters and conditionals can be added later to provide more flexibility between environments.

## Code Reuse
I noticed that the five tagged resources in the sample template all used the same five tags and that the Tags() object constructor accepts a dictionary as an agrument, so I defined the dictionary **resource_tags** at the beginning of the script with default values assigned for each key. Then, prior to constructing each resource object, I simply update the **resource_tags** dictionary entries that are unique to the resource (in this case, "Name"). This will also make it easier to modify the script for deployment to other environments and VPCs.
## Catching Missing Data
### Problem
Troposphere allows for the creation of resource objects with just a title. For example,
```python
cloudwatch_alarm_topic = sns.Topic("CloudWatchAlarmTopic")
```
And because all that is required for the resource object to be valid in the CloudFormation Template is a title, the following is also valid:
```python
template.add_resource(cloudwatch_alarm_topic)
```
This becomes a very real problem in any scenario where a property is not required by CloudFormation but represents a business or operational requirement to the organization. The script would generate a valid template without error or warning.
### Solution
1. Abstract the properties for each resource being created into a separate dictionary
1. In the constructor for the resource object, pass in dictionary.get("PropertyName") for the value of each keyword argument, where:
    * **dictionary** is the name of the properties dictionary previously declared
    * **PropertyName** is the argument keyword

This ensures that if a desired property is not included, the result passed from the get() function raises a TypeError exception and the template is not generated.

*Note: Due to time constraints, this has only been implemented for the **BastionSG** resource declaration*

