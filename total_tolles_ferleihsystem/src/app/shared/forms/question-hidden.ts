import { QuestionBase, QuestionOptions } from './question-base';

export class HiddenQuestion extends QuestionBase<any> {
    controlType = 'hidden';

    constructor(options: QuestionOptions = {}) {
        super(options);
    }
}