class MayekBot {
    static MayekMessages = {
        'title': 'Transliterate to Bengali',
        'title.placeholder': 'Title',
        'title.label': 'Title',
        'content.label': 'Content',
        'content.placeholder': 'The content in Bengali script',
        'content.help': 'The content in Bengali script',
        'summary.label': 'Summary',
        'summary.placeholder': 'A short summary of the changes',
        'summary.help': 'A short summary of the changes',
        'submit.label': 'Submit',
        'cancel.label': 'Cancel',
        'error': 'Error:',
        'error.titleAlreadyBengali': 'The title is already in Bengali',
        'error.notMainNamespace': 'Not running on page because it is not in the main namespace',
        'error.notArticle': 'Not running on page because it is not an article',
        'error.notEditing': 'Not running on page because it is not being edited',
        'prompt': 'Do you want your changes to be transliterated to Bengali as well?',
        'success': 'Successfully transliterated to Bengali. The page is at ',
        'error.api': 'Error: ',
    };
    static injectStyle() {
        const styleID = 'mayek-bot-style';
        const styleClass = 'mayek-bot-dialog';
        if (!document.getElementById(styleID)) {
            const style = document.createElement('style');
            style.id = styleID;
            style.innerHTML = `
            .${styleClass} {
                padding: 10px;
            }
            `;
            document.head.appendChild(style);
        }
        return styleClass;
    }
    static showEditDialog({ onCancel, onSubmit }) {
        const styleClass = MayekBot.injectStyle();
        const transliteratedTitleInput = new OO.ui.TextInputWidget({
            placeholder: MayekBot.MayekMessages['title.placeholder'],
            disabled: true
        });
        const contentInput = new OO.ui.MultilineTextInputWidget({
            rows: 10,
            placeholder: MayekBot.MayekMessages['content.placeholder'],
            autosize: true,
            help: MayekBot.MayekMessages['content.help'],
            disabled: true

        });
        const summaryInput = new OO.ui.TextInputWidget({
            placeholder: MayekBot.MayekMessages['summary.placeholder'],
            help: MayekBot.MayekMessages['summary.help'],
            disabled: true
        });
        const submitButton = new OO.ui.ButtonWidget({
            label: MayekBot.MayekMessages['submit.label'],
            flags: ['primary', 'progressive'],
            disabled: true
        });
        const cancelButton = new OO.ui.ButtonWidget({
            label: MayekBot.MayekMessages['cancel.label'],
            flags: ['destructive'],
        });
        const progressBar = new OO.ui.ProgressBarWidget({
            progress: false
        });
        const fields = [
            progressBar,
            new OO.ui.FieldLayout(transliteratedTitleInput, {
                label: MayekBot.MayekMessages['title.label'],
                align: 'top',
            }),
            new OO.ui.FieldLayout(contentInput, {
                label: MayekBot.MayekMessages['content.label'],
                align: 'top',

            }),
            new OO.ui.FieldLayout(summaryInput, {
                label: MayekBot.MayekMessages['summary.label'],
                align: 'top',
            }),
            new OO.ui.ActionFieldLayout(
                cancelButton,
                submitButton
            )
        ]
        const fieldset = new OO.ui.FieldsetLayout({
            items: fields,
            label: MayekBot.MayekMessages['title'],
            classes: [styleClass]
        });
        // Creating and opening a simple dialog window.
        // Subclass Dialog class. Note that the OOjs inheritClass() method extends the parent constructor's prototype and static methods and properties to the child constructor. 
        function MyDialog(config) {
            MyDialog.super.call(this, config);
        }
        OO.inheritClass(MyDialog, OO.ui.Dialog);

        // Specify a name for .addWindows()
        MyDialog.static.name = 'transliterationDialog';
        // Specify a title statically (or, alternatively, with data passed to the opening() method).
        MyDialog.static.title = MayekBot.MayekMessages['title'];

        // Customize the initialize() function: This is where to add content to the dialog body and set up event handlers.
        MyDialog.prototype.initialize = function () {
            // Call the parent method.
            MyDialog.super.prototype.initialize.call(this);
            // Create and append a layout and some content.
            this.content = fieldset;
            // this.content.$element.append('<p>A simple dialog window. Press \'Esc\' to close. </p>');
            this.$body.append(this.content.$element);
        };

        // Override the getBodyHeight() method to specify a custom height (or don't to use the automatically generated height).
        MyDialog.prototype.getBodyHeight = function () {
            return this.content.$element.outerHeight(true);
        };

        // Make the window.
        var myDialog = new MyDialog({
            size: 'large',
            styles: {
                'padding': '10px',
            }
        });
        // Create and append a window manager, which will open and close the window.
        var windowManager = new OO.ui.WindowManager();
        $(document.body).append(windowManager.$element);

        // Add the window to the window manager using the addWindows() method.
        windowManager.addWindows([myDialog]);

        // Open the window!
        windowManager.openWindow(myDialog);
        cancelButton.on('click', function () {
            onCancel().then(e => windowManager.closeWindow(myDialog));
        });
        submitButton.on('click', function () {
            progressBar.toggle(true);
            submitButton.setDisabled(true);
            cancelButton.setDisabled(true);
            contentInput.toggle(false);// Disable the content input
            summaryInput.setDisabled(true);
            transliteratedTitleInput.setDisabled(true);
            onSubmit({
                title: transliteratedTitleInput.getValue(),
                content: contentInput.getValue(),
                summary: summaryInput.getValue()
            }).then(e => windowManager.closeWindow(myDialog));
        });
        const loaded = function ({ title, content, summary }) {
            // Enable all the inputs
            transliteratedTitleInput.setDisabled(false);
            contentInput.setDisabled(false);
            summaryInput.setDisabled(false);
            submitButton.setDisabled(false);

            transliteratedTitleInput.setValue(title);
            contentInput.setValue(content);
            summaryInput.setValue(summary);
            progressBar.toggle(false);
        }
        return loaded;
    }
    static runMayekBot() {
        const namespace = mw.config.get('wgCanonicalNamespace') == '';
        // const action = mw.config.get('wgAction') == 'edit';
        const isArticle = mw.config.get('wgIsArticle') || true;
        if (namespace === false) {
            console.log(MayekBot.MayekMessages['error.notMainNamespace']);
            return;
        }
        if (isArticle === false) {
            console.log(MayekBot.MayekMessages['error.notArticle']);
            return;
        }
        const submitButton = document.querySelector('button.save.submit.cdx-button,input#wpSave');
        const editIcon = document.querySelector('a#ca-edit');
        const APIURL = "https://mayek-bot-nokib.toolforge.org/api/transliterate";
        async function transliterate(text) {
            const f = new FormData();
            f.append("text", text);
            const response = await fetch(APIURL, {
                "credentials": "include",
                "method": "POST",
                "mode": "cors",
                "body": f
            });
            return await response.text();
        }
        if (editIcon) {
            editIcon.addEventListener('click', function () {
                const timer = setInterval(function () {
                    const submitButton = document.querySelector('button.save.submit.cdx-button,input#wpSave');
                    if (submitButton) {
                        submitButton.onclick = onClick();
                        clearInterval(timer);
                    };
                }, 1000);
            });
        }
        const previousOnclick = submitButton?.onclick;
        function onClick() {
            let done = false;
            return async (e) => {
                if (done === false && confirm(MayekBot.MayekMessages['prompt'])) {
                    try {
                        e.preventDefault();
                        e.stopPropagation();
                        const title = mw.config.get('wgPageName');
                        const username = mw.config.get('wgUserName');
                        const contentBox = document.querySelector('textarea#wpTextbox1, textarea#wikitext-editor');
                        const summaryBox = document.querySelector('input#wpSummary,div.summary > textarea');
                        const minorEditBox = document.querySelector('input#wpMinoredit');
                        const resultLoaded = MayekBot.showEditDialog({
                            onCancel: async () => {
                                done = true;
                                return e.target.click();
                            },
                            onSubmit: async ({
                                title,
                                content,
                                summary
                            }) => {
                                try {
                                    const api = new mw.Api();
                                    const resp = await api.postWithEditToken({
                                        action: 'edit',
                                        title: title,
                                        text: content,
                                        summary: summary,
                                        minor: minorEditBox?.checked
                                    })
                                    if (resp.error) {
                                        throw new Error(resp.error.info);
                                    }
                                    if (resp.edit && resp.edit.result === 'Success') {
                                        alert(MayekBot.MayekMessages['success'] + title);
                                    }
                                } catch (e) {
                                    alert(MayekBot.MayekMessages['error.api'] + e.message);
                                } finally {
                                    done = true;
                                    e.target.click();
                                }
                            }
                        })
                        const transliteratedTitle = await transliterate(title);
                        if (transliteratedTitle === title) {
                            throw new Error(MayekBot.MayekMessages['error.titleAlreadyBengali']);
                        }
                        const transliteratedContent = await transliterate(contentBox.value);
                        const summary = summaryBox.value;
                        const summaryTransliterated = await transliterate(summary);

                        const minorEdit = minorEditBox?.checked;
                        resultLoaded({
                            title: transliteratedTitle,
                            content: transliteratedContent,
                            summary: summaryTransliterated,
                            minorEdit
                        });
                    } catch (e) {
                        alert(MayekBot.MayekMessages['error'] + e.message);
                        done = true;
                        e.target.click();
                    }
                }
                if (previousOnclick)
                    await previousOnclick();
            }

        }
        if (submitButton)
            submitButton.onclick = onClick();
    };
}






mw.loader.using('oojs-ui-windows').done(MayekBot.runMayekBot);