import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';


@Injectable()
export class StagingService {

    private STAGED_KEY = 'STAGED'

    private staged: Set<number>;

    private stagedSource = new BehaviorSubject<Set<number>>(new Set<number>());

    currentStaged = this.stagedSource.asObservable();

    constructor() {
        this.loadStaged();
        this.currentStaged.subscribe(this.saveStaged);
    }

    private loadStaged() {
        if (this.staged == null) {
            const savedStaged = localStorage.getItem(this.STAGED_KEY);
            if (savedStaged != null) {
                try {
                    const parsed = JSON.parse(savedStaged);
                    this.staged = new Set<number>(parsed);
                } catch (error) {
                    this.staged = new Set<number>();
                }
            } else {
                this.staged = new Set<number>();
            }
            this.stagedSource.next(this.staged);
        }
    }

    private saveStaged(staged: Set<number>) {
        const asList = [];
        staged.forEach(value => asList.push(value));
        localStorage.setItem(this.STAGED_KEY, JSON.stringify(asList));
    }

    stage(item_id: number) {
        this.loadStaged();
        this.staged.add(item_id);
        this.stagedSource.next(this.staged);
    }

    remove(item_id: number) {
        this.loadStaged();
        this.staged.delete(item_id);
        this.stagedSource.next(this.staged);
    }

    isStaged(item_id): boolean {
        this.loadStaged();
        return this.staged.has(item_id);
    }

}
