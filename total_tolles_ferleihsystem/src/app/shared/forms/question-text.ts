import { QuestionBase, QuestionOptions } from './question-base';

export class TextQuestion extends QuestionBase<string> {
    controlType = 'text';
    type: string;

    constructor(options: QuestionOptions = {}) {
        super(options);
        this.type = 'textarea';
        this.nullValue = '';
    }
}
