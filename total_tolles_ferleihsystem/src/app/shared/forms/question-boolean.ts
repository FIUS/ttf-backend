import { QuestionBase, QuestionOptions } from './question-base';

export class BooleanQuestion extends QuestionBase<boolean> {
    controlType = 'boolean';
    type: 'checkbox';

    constructor(options: QuestionOptions = {}) {
        super(options);
        this.type = options['type'] || 'checkbox';
        this.nullValue = options.nullValue || false;
        this.nullable = true;
    }
}
