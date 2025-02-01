# OrderLog

テスト環境を用意しています。実際に操作してみたい場合は「2.使い方」を参照してください

## 目次

1. インストール方法
2. 使い方
3. 機能抜粋

## インストール方法

1. 環境

    `OS`

    - Mac OS(Windows上での動作確認はしていません)

    `フレームワーク`

    - Django 4.2.18
    - DB SQlite3

    `ライブラリ`

    - Django==4.2.18
    - django-crispy-forms==2.3
    - django-widget-tweaks==1.5.0
    - django-ckeditor==6.7.2
    - Markdown==3.7
    - PyPDF2==3.0.1

2. インストール手順

    1. git clone https://github.com/noknok06/JobHab.git
    2. python manage.py makemigrations
    3. python manage.py migrate
    4. python manage.py createsuperuser(Userがないと使えません)
    5. python manage.py runserver

## 使い方

テスト環境　https://hondy.pythonanywhere.com/hab/

テストユーザー　ID test@test.test / PW test

<img width="1573" alt="image" src="https://github.com/user-attachments/assets/426a1eb4-a1a2-476c-89cc-01b41984bdf2" />

### 基本機能

1. 注文管理
2. プロジェクトマネジメント
3. PDF結合ツール
4. ログ管理
5. ノート
6. 管理画面

それぞれの機能はテスト環境のノートにて確認できます。

## 機能抜粋

- 注文一覧
  <img width="1341" alt="image" src="https://github.com/user-attachments/assets/4801d102-1a53-4121-85a9-703e3bb6e646" />

- プロジェクトダッシュボード
  <img width="1370" alt="image" src="https://github.com/user-attachments/assets/b723c455-152f-4a54-9dd7-89c3721ac6e3" />

- ノート
  <img width="1037" alt="image" src="https://github.com/user-attachments/assets/695a0180-e82d-462f-a07d-0279e960185a" />
