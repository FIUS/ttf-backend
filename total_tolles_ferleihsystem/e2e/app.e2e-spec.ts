import { TTFUiPage } from './app.po';

describe('ttf-ui App', () => {
  let page: TTFUiPage;

  beforeEach(() => {
    page = new TTFUiPage();
  });

  it('should display welcome message', done => {
    page.navigateTo();
    page.getParagraphText()
      .then(msg => expect(msg).toEqual('Welcome to app!!'))
      .then(done, done.fail);
  });
});
