import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';
import { addIcons } from 'ionicons';
import {
  menuOutline,
  cartOutline,
  homeOutline,
  receiptOutline,
  personOutline,
  logOutOutline,
  bicycleOutline,
  settingsOutline,
  trashOutline,
  checkmarkCircleOutline,
  arrowBackOutline,
  addOutline,
  removeOutline,
  sadOutline,
  personCircleOutline,
  closeOutline,
  searchOutline,
  addCircleOutline,
  createOutline
} from 'ionicons/icons';

// Registrar todos os ícones usados no app
addIcons({
  'menu-outline': menuOutline,
  'cart-outline': cartOutline,
  'home-outline': homeOutline,
  'receipt-outline': receiptOutline,
  'person-outline': personOutline,
  'log-out-outline': logOutOutline,
  'bicycle-outline': bicycleOutline,
  'settings-outline': settingsOutline,
  'trash-outline': trashOutline,
  'checkmark-circle-outline': checkmarkCircleOutline,
  'arrow-back-outline': arrowBackOutline,
  'add': addOutline,
  'remove': removeOutline,
  'sad-outline': sadOutline,
  'person-circle-outline': personCircleOutline,
  'close-outline': closeOutline,
  'search-outline': searchOutline,
  'add-circle-outline': addCircleOutline,
  'create-outline': createOutline,
  'menu': menuOutline,
  'person-circle': personCircleOutline
});

bootstrapApplication(AppComponent, {
  providers: [
    ...appConfig.providers,
    provideHttpClient(withInterceptorsFromDi())
  ]
})
.catch((err) => console.error(err));