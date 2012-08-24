requirejs.config({
	paths: {
		jquery: 'lib/jquery',
		lodash: 'lib/lodash',
		underscore: 'lib/lodash',
		backbone: 'lib/backbone',
		knockout: 'lib/knockout',
		knockback: 'lib/knockback',
		text: 'lib/text',
		bootstrap: 'lib/bootstrap',
		template: window.SCRIPT_ROOT+'/template'
	},
	shim: {
		'backbone': {
			deps: ['jquery','underscore'],
			exports: 'Backbone'
		}
	}
});

require([
		'jquery', 'underscore', 'backbone',	'router'
],
function($, _, Backbone, Router) {
	$(function() {
			new Router();
			Backbone.history.start();
	});
});
