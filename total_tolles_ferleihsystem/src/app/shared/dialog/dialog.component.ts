import { Component, Input } from '@angular/core';

@Component({
    selector: 'ttf-dialog',
    templateUrl: './dialog.component.html',
    styleUrls: ['./dialog.component.scss']
})
export class myDialogComponent {
    @Input() closable: boolean = true;
    @Input() dialogType: string = 'info';
    @Input() icon: string = 'none';
    @Input() valid: boolean = true;
    @Input() okCallback: () => void = () => {};
    @Input() cancelCallback: () => void = () => {};

    private isOpen: boolean = false;

    open() {
        this.isOpen = true;
    }

    close(event?) {
        if (event != null && event.defaultPrevented) {
            return;
        }
        if (this.closable || this.dialogType === 'info') {
            this.cancel();
        }
    }

    cancel() {
        this.isOpen = false;
        this.cancelCallback();
    }

    ok() {
        if (!(this.dialogType === 'save-cancel' || this.dialogType === 'save') ||
            this.valid) {
            this.isOpen = false;
            this.okCallback();
        }
    }
}
