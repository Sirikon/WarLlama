'use strict';

const gulp = require('gulp');
const sass = require('gulp-sass');
const sourcemaps = require('gulp-sourcemaps');

const SASS_ENTRY_POINT = './src_front/sass/main.scss';
const SASS_SOURCES = './src_front/sass/**/*.scss';

gulp.task('sass:dev', () => {
    return gulp.src(SASS_ENTRY_POINT)
        .pipe(sourcemaps.init())
        .pipe(sass().on('error', sass.logError))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest('./src/Alpaca/static'));
});

gulp.task('watch', () => {
    gulp.watch(SASS_SOURCES, ['sass:dev']);
})

gulp.task('default', ['sass:dev', 'watch']);
