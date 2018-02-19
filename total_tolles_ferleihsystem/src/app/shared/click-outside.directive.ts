import { Directive, ElementRef, Output, EventEmitter, HostListener } from '@angular/core';

// based on: christianliebel.com/2016/05/angular-2-a-simple-click-outside-directive/
// and: stackoverflow.com/questions/35712379/how-can-i-close-a-dropdown-on-click-outside

@Directive({
    selector: '[clickOutside]'
})
export class ClickOutsideDirective {
    @Output() clickOutside: EventEmitter<any> = new EventEmitter();

    constructor(private _elementRef: ElementRef) {}

    @HostListener('document:click', ['$event', '$event.target'])
    public onClick($event, targetElement) {
        const isClickedInside = this._elementRef.nativeElement.contains(targetElement);
        if (!isClickedInside) {
            this.clickOutside.emit($event);
        }
    }
}
