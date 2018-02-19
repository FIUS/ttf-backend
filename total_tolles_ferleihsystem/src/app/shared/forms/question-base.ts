
export interface QuestionOptions {
    value?: any;
    valueType?: string;
    key?: string,
    label?: string,
    required?: boolean,
    readOnly?: boolean,
    min?: number | string,
    max?: number | string,
    pattern?: string,
    options?: Array<any>,
    nullValue?: any,
    isArray?: boolean,
    order?: number,
    controlType?: string;
}

export class QuestionBase<T>{
    value: T;
    valueType: string;
    key: string;
    label: string;
    required: boolean;
    readOnly: boolean;
    min: number | string | undefined;
    max: number | string | undefined;
    pattern: string | undefined;
    options: Array<T> | undefined;
    nullValue: T | undefined;
    isArray: boolean;
    order: number;
    controlType: string;

    constructor(options: QuestionOptions = {}) {
        this.value = (options.value as T);
        this.valueType = options.valueType || 'any';
        this.key = options.key || '';
        this.label = options.label || '';
        this.required = !!options.required;
        this.readOnly = !!options.readOnly;
        this.min = options.min;
        this.max = options.max;
        this.nullValue = options.nullValue;
        this.isArray = options.isArray == undefined ? false : true;
        this.order = options.order === undefined ? 1 : options.order;
        this.controlType = options.controlType || '';
    }
}