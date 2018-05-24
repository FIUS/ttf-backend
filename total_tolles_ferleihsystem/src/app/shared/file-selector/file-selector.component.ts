import { Component, Input, Output, EventEmitter, ViewChild } from '@angular/core';



@Component({
  selector: 'ttf-file-selector',
  templateUrl: './file-selector.component.html'
})
export class FileSelectorComponent {

    @Input() allowedMimeTypes: Set<string> = new Set<string>(['application/pdf']);
    @Output() file: EventEmitter<File> = new EventEmitter<File>();

    @ViewChild('fileInput') fileInput;

    selectedFile: File;

    dragover: boolean = false;

    hover: boolean = false;

    constructor() { }

    getAcceptedFiles() {
        let accepted = '';
        this.allowedMimeTypes.forEach(type => {
            if (accepted.length > 0) {
                accepted += ', ';
            }
            accepted += type;
        })
        return accepted
    }


    selectFilesFromDialog = () => {
        if (this.fileInput != null && this.fileInput.nativeElement != null
            && this.fileInput.nativeElement.files != null) {
            Array.prototype.forEach.call(this.fileInput.nativeElement.files, (file: File) => {
                if (this.allowedMimeTypes.size === 0 || this.allowedMimeTypes.has(file.type)) {
                    this.file.emit(file);
                }
            });
        }
    }


    onDropFile(event: DragEvent) {
        event.preventDefault();
        Array.prototype.forEach.call(event.dataTransfer.files, (file: File) => {
            if (this.allowedMimeTypes.size === 0 || this.allowedMimeTypes.has(file.type)) {
                this.file.emit(file);
            }
        });
    }

    onDragOverFile(event) {
        event.stopPropagation();
        event.preventDefault();
    }

}
