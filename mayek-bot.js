
function setup(){
    function MyDialog( config ) {
        MyDialog.super.call( this, config );
    }
    OO.inheritClass( MyDialog, OO.ui.Dialog );
    MyDialog.static.name = 'myDialog';
    MyDialog.prototype.initialize = function () {
        MyDialog.super.prototype.initialize.call( this );
        this.content = new OO.ui.PanelLayout( { padded: true, expanded: false } );
        this.content.$element.append( '<p>A simple dialog window. Press Escape key to ' +
            'close.</p>' );
            const button = new OO.ui.ButtonWidget( {
                label: 'Button with Icon',
                icon: 'translation',
                title: 'Remove',
                flags: [
                    'primary',
                    'progressive'
                ]
            } );
            this.content.$element.append( button.$element );
        this.$body.append( this.content.$element );
    };
    MyDialog.prototype.getBodyHeight = function () {
        return this.content.$element.outerHeight( true );
    };
    return MyDialog;
}
function runMayekBot() {
    if (mw.config.get('wgCanonicalNamespace') !== "") {

        // Only run on pages in the main namespace
        console.log('Mayek Bot: Not running on page ' + mw.config.get('wgPageName') + ' because it is in the ' + mw.config.get('wgCanonicalNamespace') + ' namespace');
        return;
    }
    // if(mw.config.get('wgIsArticle') == false){
    //     // Only run on articles
    //     console.log('Mayek Bot: Not running on page ' + mw.config.get('wgPageName') + ' because it is not an article');
    //     return;
    // }
    // if (mw.config.get('wgAction') !== "edit") {
    //     // Only run when editing
    //     console.log('Mayek Bot: Not running on page ' + mw.config.get('wgPageName') + ' because it is not being edited');
    //     return;

    // }
    const MyDialog = setup();
    const editForm = document.getElementById('editform');
    const onSubmit = editForm.onsubmit;
    ///////////
    
    const myDialog = new MyDialog( {
        size: 'medium'
    } );
    // Create and append a window manager, which opens and closes the window.
    const windowManager = new OO.ui.WindowManager();
    $( document.body ).append( windowManager.$element );
    windowManager.addWindows( [ myDialog ] );
    windowManager.openWindow( myDialog );
    // Open the window!
    
    //////////
    editForm.onsubmit = function (event) {
        event.preventDefault();
        const content = document.getElementById('wpTextbox1').value;
        const summary = document.getElementById('wpSummary').value;
        const token = mw.user.tokens.get('csrfToken');
        
    };
}
mw.loader.using('oojs-ui-core').done(runMayekBot);