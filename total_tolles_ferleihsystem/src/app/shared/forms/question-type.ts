import { QuestionBase, QuestionOptions } from './question-base';
import { ApiObject } from '../rest/api-base.service';

export class TypeQuestion extends QuestionBase<ApiObject> {
    controlType = 'type';
    type: 'type';

    constructor(options: QuestionOptions = {}) {
        super(options);
        this.type = options['type'] || 'reference';
        this.nullValue = options.nullValue || -1;
    }
}
