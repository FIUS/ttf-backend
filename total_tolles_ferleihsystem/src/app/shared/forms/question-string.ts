import { QuestionBase, QuestionOptions } from './question-base';

export class StringQuestion extends QuestionBase<string> {
    controlType = 'string';
    type: string;

    constructor(options: QuestionOptions = {}) {
        super(options);
        this.type = options['type'] || '';
        this.pattern = options.pattern;
        this.nullValue = '';
    }
}
