import {Component, ViewChild, ViewEncapsulation, OnInit, Output, EventEmitter, OnDestroy} from '@angular/core';
import {Scanner, Camera} from 'instascan';


export interface ScanResult {
    type: string;
    id: number;
}

@Component({
    selector: 'ttf-qr',
    templateUrl: './qr.component.html',
    encapsulation: ViewEncapsulation.None,
})
export class QrComponent implements OnInit, OnDestroy {

    @Output() scanResult: EventEmitter<ScanResult> = new EventEmitter<ScanResult>();

    scanner: Scanner;
    cameras: any[];
    camera: number = -1;

    @ViewChild('video') preview;

    ngOnInit() {
        console.log(this.preview);
        this.scanner = new Scanner({
            video: this.preview.nativeElement,
            backgroundScan: true,
            scanPeriod: 3,
        });
        Camera.getCameras().then((cameras) => {
            this.cameras = cameras;
            this.switchCamera();
        }).catch((e) => {
            console.error(e);
        });
        this.scanner.addListener('scan', (content) => {
            console.log(content);
        });
    }

    ngOnDestroy() {
        this.scanner.stop();
    }

    switchCamera() {
        if (this.cameras.length > 0) {
            this.camera = (this.camera + 1) % this.cameras.length;
            this.scanner.start(this.cameras[this.camera]);
        } else {
            console.error('No cameras found.');
        }
    }
}
