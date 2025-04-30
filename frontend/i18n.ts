import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import commonRu from './locales/ru/common.json';
import commonEn from './locales/en/common.json';
import commonSl from './locales/sl/common.json';

i18n.use(initReactI18next).init({
  resources: {
    ru: { common: commonRu },
    en: { common: commonEn },
    sl: { common: commonSl },
  },
  lng: 'sl',
  fallbackLng: 'ru',
  ns: ['common'],
  defaultNS: 'common',
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
