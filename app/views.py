from datetime import datetime
from decimal import Decimal

from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import CreateView
from django.views.generic import DetailView, UpdateView, ListView, FormView
from django.shortcuts import render

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, SessionNotCreatedException, ElementNotVisibleException
from selenium.webdriver.common import keys

from telegram.ext import Updater

from .models import User, PredictionBK, Link
from .forms import UserCreateForm, ProfileUpdateForm, PredictionForm

updater = Updater(token=settings.TG_TOKEN, use_context=True)


def home(request):
    return render(request, 'app/base.html')


class UserCreateView(CreateView):
    template_name = 'auth/registration.html'
    form_class = UserCreateForm
    success_url = '/'


def init_driver():
    chrome_option = webdriver.ChromeOptions()
    # chrome_option.add_argument("headless")
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_option.add_experimental_option("prefs", prefs)

    try:
        driver = webdriver.Chrome(options=chrome_option)
    except SessionNotCreatedException:
        print("Ошибка инициализации браузера. Скорее всего у вас не установлен браузер. "
              "Пожалуйста обратитесь к разработчику парсера")

    return driver


def parse(driver, request):
    wait = WebDriverWait(driver, 2)
    driver.get('https://www.kayak.com/')
    login = driver.find_element_by_id('login-username1')
    login.clear()
    login.send_keys("killvol")

    login = driver.find_element_by_id('login-password1')
    login.clear()
    login.send_keys("")

    driver.find_elements_by_name('login-submit')[1].click()

    for link in Link.objects.order_by('-password', '-id'):
        if link.link != '':
            driver.get("https://www.oddsportal.com/profile/{}/my-predictions/next/".format(link.link))

            picks_dict = {}
            picks = driver.find_elements_by_class_name('pred-usertip')
            current_user = 'killvol'
            if not picks and link.password and driver.find_element_by_class_name('cms').text.startswith(
                    'This users profile is private.') and link.link != 'killvol':
                driver.get('https://www.oddsportal.com/logout/')
                driver.get('https://www.oddsportal.com/login/')
                while True:
                    try:
                        login = wait.until(EC.visibility_of_all_elements_located((By.ID, "login-username1")))[0]
                        break
                    except TimeoutException:
                        continue
                login.clear()
                login.send_keys(link.link)

                login = driver.find_element_by_id('login-password1')
                login.clear()
                login.send_keys(link.password)

                driver.find_elements_by_name('login-submit')[1].click()
                driver.get("https://www.oddsportal.com/profile/{}/my-predictions/next/".format(link.link))
                picks_dict = {}
                picks = driver.find_elements_by_class_name('pred-usertip')
                current_user = link.link

            for pick_ind, pick in enumerate(picks):
                tds = pick.find_elements_by_tag_name('td')
                for ind, td in enumerate(tds):
                    if td.text:
                        picks_dict['pick'+str(pick_ind)] = ind

            odds = driver.find_elements_by_class_name('number2')
            odds_list = []
            for odd in odds:
                odds_list.append(odd.get_attribute('href'))

            if current_user != 'killvol':
                driver.get('https://www.oddsportal.com/logout/')
                driver.get('https://www.oddsportal.com/login/')

                while True:
                    try:
                        login = wait.until(EC.visibility_of_all_elements_located((By.ID, "login-username1")))[0]
                        break
                    except:
                        continue

                login.clear()
                login.send_keys("killvol")

                login = driver.find_element_by_id('login-password1')
                login.clear()
                login.send_keys("888ksin888")

                driver.find_elements_by_name('login-submit')[1].click()
            url = driver.current_url.split('#')[0]
            for ind in range(len(odds_list)):
                driver.get(odds_list[ind])
                if driver.current_url.split('#')[0] == url:
                    driver.refresh()
                remove = False
                try:
                    remove = wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//*[contains(@class, 'ico-remove')]")))
                except TimeoutException:
                    pass
                if not remove:
                    try:
                        add = wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//*[contains(@class, 'ico-add')]")))[picks_dict['pick'+str(ind)]].click()
                    except (TimeoutException, ElementNotVisibleException):
                        print('TimeoutException')
                while True:
                    try:
                        driver.find_element_by_tag_name('body').send_keys(keys.Keys.HOME)
                        wait.until(EC.visibility_of_all_elements_located((By.LINK_TEXT, "Save as predictions")))[0].click()
                        break
                    except TimeoutException:
                        try:
                            wait.until(EC.visibility_of_all_elements_located((By.LINK_TEXT, "Save as predictions")))[0].click()
                            break
                        except TimeoutException:
                            break
                while True:
                    try:
                        wait.until(EC.visibility_of_all_elements_located((By.LINK_TEXT, "Save as predictions")))[0].click()
                        break
                    except (TimeoutException, ElementNotVisibleException):
                        try:
                            text = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "coupon-savepreds-wrapper")))[0].text
                            if text.startswith('None of your tips can be saved '):
                                break
                        except TimeoutException:
                            break
                while True:
                    try:
                        wait.until(EC.visibility_of_all_elements_located((By.ID, "coupon-arrow")))[0].click()
                        break
                    except TimeoutException:
                        continue

                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                except:
                    pass

                menu = driver.find_element_by_id('breadcrumb')
                lis = menu.find_elements_by_tag_name('a')

                prediction, _ = Prediction.objects.get_or_create(
                    user=link.link,
                    date=datetime.strptime(','.join(driver.find_element_by_class_name('date').text.split(',')[1:]),
                                           ' %d %b %Y, %H:%M'),
                    sport=lis[1].text,
                    league=lis[-1].text,
                    teams=driver.find_element_by_tag_name('h1').text,
                    prediction='PIC' + str(picks_dict['pick'+str(ind)]),
                    match_result='-',
                    link=driver.current_url[:-1]
                )
                rows = driver.find_elements_by_class_name('lo')
                for row in rows:
                    if row.text:
                        tds = row.find_elements_by_class_name('odds')
                        bk_name = row.find_element_by_class_name('l')
                        try:
                            PredictionBK.objects.get_or_create(
                                prediction = prediction,
                                name = bk_name.text.strip(),
                                coefficient = tds[picks_dict['pick'+str(ind)]].text
                            )
                        except:
                            pass
                url = driver.current_url.split('#')[0]
    return


def run(request):
    driver = init_driver()
    parse(driver, request)
    driver.quit()
    return HttpResponse('ok')


def parse2(driver):
    wait = WebDriverWait(driver, 2)
    driver.get('https://www.oddsportal.com/login/')
    login = driver.find_element_by_id('login-username1')
    login.clear()
    login.send_keys("")

    login = driver.find_element_by_id('login-password1')
    login.clear()
    login.send_keys("")

    while True:
        try:
            wait.until(EC.visibility_of_all_elements_located((By.NAME, "login-submit")))[1].click()
            break
        except (TimeoutException, IndexError):
            continue

    c = Prediction.objects.filter(prediction_result=None, date__lt=datetime.now()).count()

    page_number = 1
    while c < 1 and page_number <= 4:
        if c <= 0: break
        driver.get('https://www.oddsportal.com/profile/killvol/my-predictions/results/page/{}/'.format(page_number))
        odds = driver.find_elements_by_class_name('number2')
        match_results = driver.find_elements_by_xpath('//td[contains(@class, "center bold")]')
        results = driver.find_elements_by_xpath(
            "//td[contains(@class, 'status-text-') or contains(@class, 'live-score')]")
        for i in range(len(results)):
            if results[i].text != 'L' and results[i].text != 'W' and not "'" in results[i].text:
                results.pop(i)

        results_dict = {}

        for ind, odd in enumerate(odds):
            results_dict[odd.get_attribute('href')] = [results[ind].text, match_results[ind].text]

        for match, res in results_dict.items():
            try:
                prediction = Prediction.objects.get(link_to_odd=match)
            except Prediction.DoesNotExist:
                continue
            if res[0] == 'W':
                prediction.prediction_result = 'Won'
            elif res[0] == 'L':
                prediction.prediction_result = 'Lose'
            prediction.match_result = res[1]
            prediction.save()
            c -= 1
            if c <= 0:
                break
        page_number += 1
    return

def run2():
    driver = init_driver()
    parse2(driver)
    driver.quit()
    return HttpResponse('ok')


def connect_to_tg(request):
    updater.bot.send_message(chat_id=settings.TG_CHAT_ID, text="""
        [inline URL](https://core.telegram.org/bots/api#formatting-options)
        """, parse_mode= 'Markdown')


class ProfileView(DetailView):
    model = User


class ProfileEditView(UpdateView):
    form_class = ProfileUpdateForm
    success_url = '/account/1'


    def get_context_data(self, **kwargs):
        context = super(ProfileEditView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

    def get_object(self, queryset=None):
        return User.objects.get(pk=self.kwargs.get('pk'))


class NextPredictionsListView(ListView):
    model = Prediction
    queryset = Prediction.objects.filter(prediction_result=None)
    template_name = 'app/prediction_next_list.html'


class LastPredictionsListView(ListView):
    queryset = Prediction.objects.filter(~Q(prediction_result=None), date__lt=datetime.now())
    template_name = 'app/prediction_last_list.html'


class CapperListView(ListView):
    model = Link
    template_name = 'app/capper_rating.html'


class PredictionCreateView(FormView):
    form_class = PredictionForm
    template_name = 'app/prediction_form.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PredictionCreateView, self).get_context_data(*args, **kwargs)
        context['predictions'] = Prediction.objects.filter(prediction_result=None, date__gt=datetime.now(), link=Link.objects.get(user=self.request.user), created=False)
        return context

    def form_valid(self, form):
        if self.request.POST.get('prediction'):
            pred = Prediction.objects.get(pk=self.request.POST.get('prediction'))
            pred.bet_amount = Decimal(self.request.POST.get('bet_amount'))
            pred.bet_coefficient = Decimal(self.request.POST.get('bet_coefficient'))
            pred.created = True
            pred.save()
            return HttpResponse('ok')
        else: return HttpResponse('not ok')

    def get_form_kwargs(self):
        form_kwargs = super(PredictionCreateView, self).get_form_kwargs()
        form_kwargs['max_amount'] = Link.objects.get(user=self.request.user).current_bank / Decimal(10)
        form_kwargs['min_amount'] = Link.objects.get(user=self.request.user).current_bank / Decimal(100)
        return form_kwargs

