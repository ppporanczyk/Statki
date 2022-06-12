Pusher.logToConsole = true;
 var app = new Vue({
    el: '#app',

    data: {
    username: {{ name|tojson }},
    alphabet: {{ alphabet|tojson }},
    players: 0,
    connectedPlayers: [],
    status: '',
    respond: 0,
    ready: 0,
    opponentReady: 0,
    pusher: new Pusher('4d2726b6eaed69e2834f', {
        authEndpoint: '/pusher/auth',
        cluster: 'eu',
        encrypted: true
    }),
    otherPlayerName: '',
    mychannel: {},
    otherPlayerChannel: {},
    turn: 0,
    mainBoxes: [[0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]],
    yourBoxes: [[0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]]
    },

    created () {
      this.subscribe();
      this.listeners();
    },

    methods: {
        subscribe: function () {
            let channel = this.pusher.subscribe('presence-channel');
            this.myChannel = this.pusher.subscribe('private-' + this.username);
            channel.bind('pusher:subscription_succeeded', (player) => {
                this.players = player.count - 1;
                player.each((player) => {
                    if (player.id != this.username){
                      this.connectedPlayers.push(player.id)}
                })
            })
            channel.bind('pusher:member_added', (player) => {
                this.players++
                this.connectedPlayers.push(player.id)
            })
            channel.bind('pusher:member_removed', (player) => {
                this.players--
                var index = this.connectedPlayers.indexOf(player.id);
                if (index > -1) {
                  this.connectedPlayers.splice(index, 1)
                }
            })
        },

        listeners: function () {
            this.pusher.bind('client-' + this.username, (message) => {
                if (confirm(message + ' zaprasza cię do gry w statki')) {
                    this.otherPlayerName = message
                    this.otherPlayerChannel = this.pusher.subscribe('private-' + this.otherPlayerName)
                    this.otherPlayerChannel.bind('pusher:subscription_succeeded', () => {
                        this.otherPlayerChannel.trigger('client-set-ships', message)
                    })
                this.setShipsOnMap() //ETAP ROZSTAWIANIA STATKOW, DODAC WALIDACJE ROZSTAWIANIA I LIMITY
                } else {
                    this.otherPlayerChannel = this.pusher.subscribe('private-' + message)
                    this.otherPlayerChannel.bind('pusher:subscription_succeeded', () => {
                        this.otherPlayerChannel.trigger('client-game-declined', "")
                    })
                  this.gameDeclined()
                }
            })

            this.myChannel.bind('client-game-declined', () => {this.status = "Odmowa bitwy"})

            this.myChannel.bind('client-set-ships', (message) => {this.setShipsOnMap()})

            this.myChannel.bind('client-is-ready', () => {this.opponentReady = 1;})

            this.myChannel.bind('client-game-started', (message) => {
                this.status = "Zaczynasz bitwe z  " + message + " twoj ruch!"
                this.turn = 1
            })

            this.myChannel.bind('client-ask-position', (data) => {this.getValueOnPos(data['yPos'], data['xPos']);})

            this.myChannel.bind('client-return-value', (data) => {this.respond = data['value'];})

            this.myChannel.bind('client-your-turn', () => {
                this.turn = 1
                this.status = "Twoj ruch!"
            })

            this.myChannel.bind('client-box-update', (update) => {this.mainBoxes = update;})

            this.myChannel.bind('client-you-lost', () => {this.gameLost();})
        },

        // Wyslanie zaproszenia do gry
        choosePlayer: function (e) {
            this.otherPlayerName = e.target.innerText
            this.otherPlayerChannel = this.pusher.subscribe('private-' + this.otherPlayerName)
            this.otherPlayerChannel.bind('pusher:subscription_succeeded', () => {
                this.otherPlayerChannel.trigger('client-' + this.otherPlayerName, this.username)
            });
        },

        // Gracz odmowil rozgrywki
        gameDeclined: function () {this.status = "Nie przyjęto zaproszenia"},

        // Set ships on the map
        setShipsOnMap: function () {this.status = "Ustaw statki na planszy. Kliknij tutaj, gdy bedziesz gotowy "},

        // Ustawianie statkow + Dodac walidacje rozstawiania
        settingAction: function (e) {
            let index = e.target.dataset.id
            let yPos = (Math.floor(index/10))-1
            let xPos = index%10 -1

            console.log(yPos + ' ' +xPos + " " + this.yourBoxes[yPos][xPos])
            if (this.yourBoxes[yPos][xPos] == 0) {
                this.yourBoxes[yPos][xPos] = 2
                e.target.style.background = 'black'
            } else if (this.yourBoxes[yPos][xPos] == 2) {
                this.yourBoxes[yPos][xPos] = 0
                e.target.style.background = 'white'
            }
        },

        // Potwierdz ulozenie planszy
        confirmSetup: function (e) {
            this.ready = 1
            if (this.opponentReady == 0){
                this.otherPlayerChannel.trigger('client-is-ready', "")
            } else{
                this.startGame()
                this.otherPlayerChannel.trigger('client-game-started', "")
            }
          },

        // rozpoczecie gry
        startGame: function () {
            this.status = "Gra zaczeta ";
            //dorobic blokowanie yourBoxes!!!!!!
        },

        // Checks to see if the play was a winning play
        playerAction: function (e) {
            let index = e.target.dataset.id
            let yPos = (Math.floor(index/10))-1
            let xPos = index%10 -1

            if (this.turn && this.mainBoxes[yPos][xPos] == 0) {
                console.log(yPos + " " +xPos)
                this.otherPlayerChannel.trigger('client-ask-position', {"yPos": yPos, "xPos": xPos})
                while (this.response!=0) {;}

                console.log("Wartosc pola " + this.respond)
                if (this.respond == 2 ){
                    this.mainBoxes[yPos][xPos] = 1
                    e.target.style.background  = 'green'
                    this.turn = 0
                    this.status = "Ruch przeciwnika!"
                } else {
                    this.mainBoxes[yPos][xPos] = -1
                    e.target.style.background  = 'red'
                    this.otherPlayerChannel.trigger('client-your-turn', "")
                }

                this.respond=0
                if (this.theresAMatch()) {
                    this.gameWon()
                    this.otherPlayerChannel.trigger('client-you-lost', '')
                }
            }
        },

        getValueOnPos: function (yPos, xPos){
            var value = this.yourBoxes[yPos][xPos]
            if (value == 2 ){
                this.yourBoxes[yPos][xPos] = 1
                this.$refs[yPos][xPos].style.background = 'green'
            } else {
                this.yourBoxes[yPos][xPos] = -1
                this.$refs[yPos][xPos].style.background = 'red'
                this.otherPlayerChannel.trigger('client-your-turn', "")
            }
        },

        getValueFromOpponent: function (value){
            console.log("Wartosc pola " + this.respond)
            if (this.respond == 2 ){
                this.mainBoxes[yPos][xPos] = 1
                this.$refs[yPos][xPos].style.background = 'green'
                this.turn = 0
                this.status = "Ruch przeciwnika!"
            } else {
                this.mainBoxes[yPos][xPos] = -1
                this.$refs[yPos][xPos].style.background = 'red'
                this.otherPlayerChannel.trigger('client-your-turn', "")
            }

            this.otherPlayerChannel.trigger('client-box-update', this.mainBoxes)
            if (this.theresAMatch()) {
                this.gameWon()
                this.otherPlayerChannel.trigger('client-you-lost', '')
            }
        },

        // sprawdza, czy wszystkie statki zostaly znalezione
        theresAMatch: function () {
            for (var i = 1; i < 9; i++) {
                for (var j = 1; j < 9; j++) {
                    if (this.mainBoxes[i][j] == 2) {  //POPRAWIC
                        return false
                    }
                }
            }
            return true
        },

        // Obecny gracz wygrywa
        gameWon: function () {
            this.status = "Wygrales!"
            this.restartGame()
        },

        // Obecny gracz przegrywa
        gameLost: function () {
            this.turn = 1;
            this.status = "Przegrales!"
            this.restartGame()
        },

        restartGame: function () {
            this.$refs.gameboard_main.classList.add('invisible');
            this.$refs.gameboard.classList.add('invisible');
                for (i = 1; i < 9; i++) {
                    for (j = 1; j < 9; j++) {
                       this.$refs[i][j].style.background  = 'white';
                       this.mainBoxes[i][j] = 0;
                       this.yourBoxes[i][j] = 0
                    }
                }
              this.$refs.gameboard_main.classList.remove('invisible');
              this.$refs.gameboard.classList.remove('invisible');
        },
    }
 });