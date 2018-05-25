import { QuestionBase, QuestionOptions } from './question-base';

export class DateTimeQuestion extends QuestionBase<string> {
    controlType = 'date-time';
    type: string;

    constructor(options: QuestionOptions = {}) {
        super(options);
        this.type = options['type'] || 'date-time';
        this.nullValue = '0001-01-01T00:00';
    }
}
