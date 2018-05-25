import { QuestionBase, QuestionOptions } from './question-base';

export class DateTimeQuestion extends QuestionBase<string> {
    controlType = 'datetime';
    type: string;

    constructor(options: QuestionOptions = {}) {
        super(options);
        this.type = options['type'] || 'datetime';
        this.nullValue = '0001-01-01';
    }
}
