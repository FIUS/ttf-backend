import { QuestionBase, QuestionOptions } from './question-base';

export class IntegerQuestion extends QuestionBase<number> {
    controlType = 'number';
    type: 'number';

    constructor(options: QuestionOptions = {}) {
        super(options);
        this.type = options['type'] || 'number';
        this.nullValue = options.nullValue || -1;
    }
}
