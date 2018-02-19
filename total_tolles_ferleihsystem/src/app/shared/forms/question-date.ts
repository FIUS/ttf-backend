import { QuestionBase, QuestionOptions } from './question-base';

export class DateQuestion extends QuestionBase<string> {
    controlType = 'date';
    type: string;

    constructor(options: QuestionOptions = {}) {
        super(options);
        this.type = options['type'] || 'date';
        this.nullValue = '0001-01-01';
    }
}