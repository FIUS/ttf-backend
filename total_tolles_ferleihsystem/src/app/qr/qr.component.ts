import {Component, ViewChild, ViewEncapsulation, OnInit, Output, EventEmitter, OnDestroy, NgZone} from '@angular/core';
import {Scanner, Camera} from 'instascan';


@Component({
    selector: 'ttf-qr',
    templateUrl: './qr.component.html',
    encapsulation: ViewEncapsulation.None,
})
export class QrComponent implements OnInit, OnDestroy {

    @Output() scanResult: EventEmitter<number> = new EventEmitter<number>();

    scanner: Scanner;
    cameras: any[];
    camera: number = -1;

    lastScan;

    @ViewChild('video') preview;

    constructor(private zone: NgZone) {}

    ngOnInit() {
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
            this.zone.run(() => {
                const result = content.match(/\/items\/([0-9]+)\/?$/);
                if (result != null && result[1] != null) {
                    this.lastScan = result[1];
                    this.scanResult.next(parseInt(result[1], 10));
                }
            });
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
