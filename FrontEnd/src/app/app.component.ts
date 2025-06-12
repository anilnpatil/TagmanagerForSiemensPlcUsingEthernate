import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { SelectConnectionComponent } from './select-connection/select-connection.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'tag-manager-app';

  constructor(private dialog: MatDialog, private router: Router) {}

  openSelectConnectionDialog(): void {
    const dialogRef = this.dialog.open(SelectConnectionComponent, {
      width: '250px'
    });

    dialogRef.afterClosed().subscribe(ipAddress => {
      if (ipAddress) {
        // Pass the selected IP address to the TagManagerComponent
        this.router.navigate(['/tag-manager'], { state: { ipAddress: ipAddress } });
      }
    });
  }
}
