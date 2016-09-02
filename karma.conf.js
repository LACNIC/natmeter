// Karma configuration
// Generated on Fri Sep 02 2016 14:19:06 GMT+0200 (SAST)

module.exports = function (config) {

    // define browsers
    config.customLaunchers = {
        bs_safari_mac: {
            base: 'BrowserStack',
            browser: 'chrome',
            browser_version: '52',
            os: 'OS X',
            os_version: 'El Capitan',
            displayName: "Chrome OSX Desktop"
        }
    }

    config.set({

        // base path that will be used to resolve all patterns (eg. files, exclude)
        basePath: '',


        // frameworks to use
        // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
        frameworks: ['jasmine'],


        // list of files / patterns to load in the browser
        files: [
            'https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js',
            'stun/app/static/app/js/stun.js',
            'stun/app/static/app/js/tests/stun.test.js'
        ],


        // list of files to exclude
        exclude: [],


        // preprocess matching files before serving them to the browser
        // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
        preprocessors: {},


        // test results reporter to use
        // possible values: 'dots', 'progress'
        // available reporters: https://npmjs.org/browse/keyword/karma-reporter
        reporters: ['progress'],


        // web server port
        port: 9876,


        // enable / disable colors in the output (reporters and logs)
        colors: true,


        // level of logging
        // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
        logLevel: config.LOG_INFO,


        // enable / disable watching file and executing tests whenever any file changes
        autoWatch: false,

        browserStack: {
            username: process.env.BS_USERNAME,
            accessKey: process.env.BS_ACCESS_KEY
        },

        // start these browsers
        // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
        browsers: [Object.keys(config.customLaunchers)],


        // Continuous Integration mode
        // if true, Karma captures browsers, runs the tests and exits
        singleRun: false
    })
}
