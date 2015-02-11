Folder Structure
================

Root Directory Structure
---------------------------

The root of your application contains the following items:

 * app - contains code related specifically to your application.
 * ferris - contains Ferris' core code.
 * plugins - contains re-usable components that you can use from your application.
 * packages - contains 3rd party libraries (such as pytz, google apis, etc.)
 * app.yaml - Normal App Engine configuration. You can modify your application configuration here.
 * settings.py - Global application (and plugin) configuration. You can load these settings by importing the settings module.


Application Directory Structure
-------------------------------

The app folder contains the following items:

 * models - Contains :doc:`model <models>` modules.
 * handlers - Contains :doc:`handler <handlers>` modules.
 * templates - Contains :doc:`template <template>` files and macros.
 * static - Contains static resources such as javascript, css, and images.
 * tests - Contains any :doc:`test specs <testing>`.
 * routes.py - Contains :doc:`route <routing>` and :doc:`plugin <plugins>` configuration. You can enable plugins and change routing rules here. As most routing happens automatically, you'll use this primarily to enable plugins.
 * listeners.py - Contains event listerers for the :doc:`global event bus <events>`. You can use this to set the applications theme and enforce application-wide security settings.
