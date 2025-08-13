# 🖥 KOS_Billing_AI_ChatBot#

## 🤔 Description
2021-1학기 모바일 앱 개발 중 외부 프로젝트로 실시된 UN 제네바 지사에서 사용할 인사과 자동 이직 시스템 입니다.<br>
현재 UN 제네바 지사의 이직 시스템은 매번 이직 시즌이 올 때마다 인사과 직원들이 수작업을 통해 이직을 희망하는 사람들의 근무지를 정하는 상황입니다.<br>
이러한 인력 낭비문제를 해결하고자 이직 알고리즘이 적용한 어플리케이션 개발을 목표로 진행된 프로젝트 입니다.<br>

- 기술 스택
  - **Android Studio**
  - **Flutter**
    - **Dart**
  - **Firebase**

> 2021.07.29 UN 제네바 지사로 프로토타입 프로그램 시연동영상 제출 및 평가 대기중
## 📌 Environment
- Win10, Mac Big Sur 11.2.3
- Android 11.0 ver
- Flutter 2.0.1 ver
  - Dart 2.12.0

## 💾 Installation

## 💡 Functions

|State Management|User Interface1|User Interface2|
|:--------------:|---------------|---------------|
|![스크린샷 2021-09-25 오전 2 28 08](https://user-images.githubusercontent.com/34247631/134716533-ee86dfcc-1d93-4b8d-9a93-bfdf7797b99f.png)|![스크린샷 2021-09-25 오전 2 27 47](https://user-images.githubusercontent.com/34247631/134716570-9298d6a1-fd3b-43d8-9ad4-88f8b2db0750.png)|![스크린샷 2021-09-25 오전 2 28 22](https://user-images.githubusercontent.com/34247631/134716625-9ac9fdf7-dc2d-4bfd-8481-f52bca738f6f.png)|
|프로젝트의 특성상 사용자가 여러 페이지를 드나들며 정보를 확인해야하는 상황이 많이 발생했습니다. 그래서 Sign-in페이지에서 provider를 사용하여 사용자 state를 관리함으로써 페이지 이동 간 state가 잘 유지 될 수 있도록 하였습니다.|손에 들어오는 핸드폰 환경이 아닌 테블릿 환경에서 작동하는 어플리케이션을 개발하는게 조건이었기 때문에 User Interface 구성에 많은 노력을 했습니다. 큰 테블릿 화면을 2~3개 영역으로 나눠서 사용자에게 효율적으로 정보를 제공할 수 있도록 하였습니다. 그리고 reorderable list를 구현하여 해당 포지션의 지원자간 Rank를 매겨 우선순위를 지정할 수 있도록 하였습니다. 드래그로 직관적으로 우선순위를 부여할 수 있다는 장점이 있습니다.|각 포지션별로 지원자간에 우선순위가 정해지면 이 우선순위를 통해 relocation algorithm을 적용하여 이직 가능한 경우의 수를 인사과 직원에게 제공해야했습니다. 그래서 본 프로젝트 가장 핵심인 기능을 구현하기 위해서 저희 팀이 구상한 알고리즘을 구현 및 프로그램에 적용하여 이 기능을 구현하였습니다. 알고리즘에 대한 설명은 [UX_Matching algorithm explanation Document](https://github.com/dprua/mobile_un_project/files/7227640/UX_Matching.algorithm.explanation.pdf)에서 확인 가능 합니다.


### 📸 Presentation
프로젝트 발표자료와 영상은 아래 링크를 통해 확인하실 수 있습니다.
- Video Rink
  - [Kor](https://youtu.be/LSlEKh-w03I), [Eng](https://youtu.be/PctKhzsiEco)
- Resources Rink
  - [Kor](https://docs.google.com/presentation/d/1RdXdpcmKTsOsRRfJfNyqB-k8X1NxXJ3Ozb7IDy6M_ao/edit?usp=sharing), [Eng](https://docs.google.com/presentation/d/1yS8-6cKfqER9V_00oiHnHGDBvchY0WMpa_4HhIFQzI0/edit?usp=sharing)

## 🙇 Contributors
|이름|분업내용|연락처|
|:-:|------|-----|
|**박예겸**|PM, HR Pages, UI design, Algorithm development|dprua@naver.com|
