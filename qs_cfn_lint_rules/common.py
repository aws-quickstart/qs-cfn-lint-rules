def search_resources_for_property_value_violations(cfn, resource_type, prop_name, expected_prop_value) -> []:
    """
    Searches all resources of resource type, to ensure property is expected value
    returns a list of paths to violating lines.
    """
    results = []
    for resource_name, resource_values in cfn.get_resources([resource_type]).items():
        path = ['Resources', resource_name, 'Properties']
        properties = resource_values.get('Properties')

        if prop_name not in properties.keys():
            results.append(path)
            return results

        if properties[prop_name] is not expected_prop_value:
            results.append(path + [prop_name])
    return results

def deep_get(source_dict, list_of_keys, default_value=None):
    x = source_dict
    for k in list_of_keys:
        if isinstance(k, int):
            x = x[k]
        else:
            x = x.get(k, {})
    if not x:
        return default_value
    return x
