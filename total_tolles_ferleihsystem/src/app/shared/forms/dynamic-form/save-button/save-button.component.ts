import { Component, Input } from '@angular/core';


@Component({
  selector: 'ttf-save-button',
  templateUrl: 'save-button.component.html',
})
export class SaveButtonComponent {


    @Input() formValid: boolean = false;

    saving: boolean = false;
    saveSuccess: boolean = false;
    saveFail: boolean = false;

    resetStatus = () => {
        this.saveSuccess = false;
        this.saveFail = false;
    }

    save = () => {
        if (!this.formValid) {
            return;
        }
        this.saving = true;
        this.saveSuccess = false;
        this.saveFail = false;
    }

    saveFinished = (success: boolean) => {
        this.saving = false;
        if (success) {
            this.saveSuccess = true;
        } else {
            this.saveFail = true;
        }
    }
}
