import { Component } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { RouterModule } from '@angular/router';
import { addIcons } from 'ionicons';
import { eye, eyeOff } from 'ionicons/icons';

@Component({
  standalone: true,
  selector: 'app-root',
  template: `<ion-app><ion-router-outlet></ion-router-outlet></ion-app>`,
  imports: [IonicModule, RouterModule]
})
export class AppComponent {
  constructor() {
    // Registrar ícones usados no app
    addIcons({
      eye: eye,
      'eye-off': eyeOff
    });
  }
}