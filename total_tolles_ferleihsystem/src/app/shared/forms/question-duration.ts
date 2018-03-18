import { QuestionBase, QuestionOptions } from './question-base';

export class DurationQuestion extends QuestionBase<number> {
    controlType = 'duration';
    type: 'number';

    constructor(options: QuestionOptions = {}) {
        super(options);
        this.type = options['type'] || 'number';
        this.nullValue = options.nullValue || -1;
    }
}
