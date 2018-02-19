import { QuestionBase, QuestionOptions } from './question-base';

export class DropdownQuestion extends QuestionBase<string> {
    controlType = 'dropdown';
    options: any[] = [];

    constructor(options: QuestionOptions = {}) {
        super(options);
        this.options = options['options'] || [];
    }
}