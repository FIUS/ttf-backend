import { Directive, ElementRef, Output, EventEmitter, HostListener } from '@angular/core';

@Directive({
    selector: '[isVisible]'
})
export class IsVisibleDirective {
    @Output() isVisible: EventEmitter<any> = new EventEmitter();

    intersectionObserverOptions = {
        root: null,
        rootMargin: '150px',
        threshold: 1.0
    }

    constructor(private _elementRef: ElementRef) {
        const observer = new IntersectionObserver((x) => {
            const isVisible = x.some((entry) => entry.intersectionRatio > 0);
            if (isVisible) {
                observer.disconnect();
                this.isVisible.emit();
            }
        }, this.intersectionObserverOptions);

        // provice the observer with a target
        observer.observe(_elementRef.nativeElement);
    }
}
