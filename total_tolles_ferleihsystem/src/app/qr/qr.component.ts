import {Component, ViewChild, ViewEncapsulation, OnInit, Output, EventEmitter, OnDestroy, NgZone} from '@angular/core';
import { BrowserQRCodeReader, Result } from '@zxing/library';
import { Subject, Subscription } from 'rxjs/Rx';
import { map, filter } from 'rxjs/operators';

class QrReader extends BrowserQRCodeReader {

    private scannerResults: Subject<Result> = new Subject();
    scannerResultsSubscription: Subscription;
    latestScanResult: Result;

    startScanning(deviceId, videoElement, ignoreRepeating: number = 5000) {
        this.reset();
        this.prepareVideoElement(videoElement);
        let constraints;
        if (undefined === deviceId) {
            constraints = {
                video: { facingMode: 'environment' }
            };
        } else {
            constraints = {
                video: { deviceId: { exact: deviceId } }
            };
        }
        const decodeOnce = () => {
            this.decodeOnceWithDelay(
                (result) => this.scannerResults.next(result),
                (err) => this.scannerResults.error(err)
            );
        };
        this.scannerResultsSubscription = this.scannerResults.asObservable().subscribe(() => {
            decodeOnce();
        });
        navigator.mediaDevices.getUserMedia(constraints)
            .then((stream) => this.startDecodeFromStream(stream, decodeOnce))
            .catch((error) => this.scannerResults.error(error));
        return this.scannerResults.asObservable().pipe(
            filter((result: Result) => {
                if (this.latestScanResult != null) {
                    if (this.latestScanResult.getText() === result.getText()) {
                        if (this.latestScanResult.getTimestamp() + ignoreRepeating > result.getTimestamp()) {
                            // skip scan result if last scan was same result and is only
                            // ignoreRepeating milliseconds from this scan result
                            return false;
                        }
                    }
                }
                this.latestScanResult = result;
                return true;
            })
        );
    }

    reset() {
        if (this.scannerResultsSubscription != null) {
            this.scannerResultsSubscription.unsubscribe();
        }
        super.reset()
    }
}


@Component({
    selector: 'ttf-qr',
    templateUrl: './qr.component.html',
    encapsulation: ViewEncapsulation.None,
})
export class QrComponent implements OnInit, OnDestroy {

    @Output() scanResult: EventEmitter<number> = new EventEmitter<number>();

    codeReader: QrReader;
    cameras: any[];
    camera: number = -1;

    scannerResults: Subject<any> = new Subject();
    scannerResultsSubscription: Subscription;

    lastScan;

    isActive = true;

    @ViewChild('video') preview;

    constructor(private zone: NgZone) {}

    ngOnInit() {
        this.codeReader = new QrReader();

        this.codeReader.getVideoInputDevices().then(videoInputDevices => {
            this.cameras = videoInputDevices;
            this.switchCamera();
        }).catch(err => console.error(err));
    }

    ngOnDestroy() {
        this.codeReader.reset();
        if (this.scannerResultsSubscription != null) {
            this.scannerResultsSubscription.unsubscribe();
        }
    }

    switchCamera() {
        if (this.cameras.length > 0) {
            this.camera = (this.camera + 1) % this.cameras.length;
            this.startScanning();
        } else {
            console.error('No cameras found.');
        }
    }

    startScanning() {
        this.codeReader.reset();
        const cameraId = this.cameras[this.camera].deviceId;
        const videoElement = this.preview.nativeElement;
        this.scannerResultsSubscription = this.codeReader.startScanning(cameraId, videoElement).pipe(
            map((result: Result) => {
                return result.getText();
            }),
        ).subscribe(this.processScanResult);
    }

    processScanResult = (content) => {
        this.zone.run(() => {
            const result = content.match(/\/items\/([0-9]+)\/?$/);
            if (result != null && result[1] != null) {
                this.lastScan = result[1];
                this.scanResult.next(parseInt(result[1], 10));
            }
        });
    }
}
