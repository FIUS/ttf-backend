import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'activeLending'
})
export class ActiveLendingPipe implements PipeTransform {
    transform(items: any[]): any {
        if (!items) {
            return items;
        }

        return items.filter(item => item.returned == null);
    }
}
