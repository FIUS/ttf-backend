export function attrDefTitle(attributeDefinition) {
    let title = attributeDefinition.name;
    try {
        const jsonscheme = JSON.parse(attributeDefinition.jsonschema);
        if (jsonscheme.title != null && jsonscheme.title !== '') {
            title = jsonscheme.title;
        }
    } catch (error) {}
    return title;
}
