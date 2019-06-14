import { Pipe, PipeTransform } from '@angular/core';
import { attrDefTitle } from './helper-functions';

@Pipe({name: 'attributeDefinitionTitle'})
export class AttributeDefinitionTitlePipe implements PipeTransform {
    transform(value): string {
        return attrDefTitle(value);
    }
}