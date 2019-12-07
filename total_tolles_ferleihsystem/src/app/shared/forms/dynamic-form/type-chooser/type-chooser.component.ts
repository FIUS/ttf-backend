import { Component, forwardRef, Input, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { ApiObject } from '../../../rest/api-base.service';
import { ApiService } from '../../../rest/api.service';

import { QuestionBase } from '../../question-base';
import { myDropdownComponent } from '../../../dropdown/dropdown.component';
import { Subscription } from 'rxjs';



@Component({
  selector: 'ttf-type-chooser',
  templateUrl: 'type-chooser.component.html',
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => TypeChooserComponent),
    multi: true
  }]
})
export class TypeChooserComponent implements ControlValueAccessor, OnInit, OnDestroy {

    private typeSubscription: Subscription;

    @ViewChild(myDropdownComponent, { static: true }) dropdown: myDropdownComponent

    @Input() question: QuestionBase<any>;
    @Input() allowDeselect: boolean = false;

    searchTerm: string = '';

    types: ApiObject[] = [];

    selected: number;
    filter: Set<number> = new Set<number>();

    highlighted: number;

    onChange: any = () => {};

    onTouched: any = () => {};

    get value(): number {
        if (this.types == undefined || this.selected == undefined) {
            return -1;
        }
        return this.selected;
    }

    @Input() set value(val: number) {
        if (val !== -1) {
            this.selected = val;
            if (this.types != null) {
                this.types.forEach(type => {
                    if (type.id === val) {
                        this.searchTerm = type.name;
                    }
                });
                this.updateFilter();
            }
        } else {
            this.selected = undefined;
            this.searchTerm = '';
            this.updateFilter();
        }
        this.onChange(this.value);
        this.onTouched();
    }

    constructor(private api: ApiService) {}

    ngOnInit(): void {
        this.typeSubscription = this.api.getItemTypes().subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.types = data;
            this.updateFilter();
        });
    }

    ngOnDestroy(): void {
        if (this.typeSubscription != null) {
            this.typeSubscription.unsubscribe();
        }
    }

    updateFilter(searchTerm?: string) {
        if (searchTerm == null) {
            searchTerm = this.searchTerm;
        }
        const filter = new Set<number>();
        this.types.forEach(type => {
            if (!type.name.toUpperCase().includes(searchTerm.toUpperCase())) {
                filter.add(type.id);
            }
        });
        this.filter = filter;
        this.updateHighlight();
    }

    updateHighlight() {
        if (this.highlighted == null || this.filter.has(this.highlighted)) {
            for (const type of this.types) {
                if (!this.filter.has(type.id)) {
                    this.highlighted = type.id;
                    return;
                }
            }
        }
    }

    select(type?: ApiObject) {
        if (type == null && this.types != null) {
            this.types.forEach(temp => {
                if (temp.id === this.highlighted) {
                    type = temp;
                }
            })
        }
        if (type == null) {
            return;
        }
        if (this.allowDeselect && this.selected == type.id) {
            this.selected = undefined;
            this.searchTerm = '';
        } else {
            this.selected = type.id;
            this.searchTerm = type.name;
        }
        this.updateFilter('');
        this.dropdown.closeDropdown();
        this.onTouched();
        this.onChange(this.value);
    }

    highlightNext() {
        let found = false;
        for (const type of this.types) {
            if (!this.filter.has(type.id)) {
                if (found) {
                    this.highlighted = type.id;
                    return;
                }
                if (this.highlighted === type.id) {
                    found = true;
                }
            }
        }
    }

    highlightPrevious() {
        let last;
        for (const type of this.types) {
            if (!this.filter.has(type.id)) {
                if (this.highlighted === type.id) {
                    this.highlighted = last;
                }
                last = type.id;
            }
        }
    }

    registerOnChange(fn) {
        this.onChange = fn;
    }

    registerOnTouched(fn) {
        this.onTouched = fn;
    }

    writeValue(value) {
        if (value) {
            this.value = value;
        }
    }
}
