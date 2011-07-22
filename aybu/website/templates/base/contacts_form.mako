<!--
<div id="result">
<h4 class="success">
<h4 class="error">
	Messaggio di successo o errore
</h4>
</div>
-->

<form id="form" method="post" action="${request.environ.get('PATH_INFO')}">
	<fieldset>
		<label for="name">${_(u'Nome')}: </label>
		<input id="name" name="name" type="text"/>

		<label for="surname">${_(u'Cognome')}: </label>
		<input id="surname" name="surname" type="text"/>

		<label for="phone">${_(u'Telefono')}: </label>
		<input id="phone" name="phone" type="text"/>

		<label for="email">${_(u'E-mail')}: </label>
		<input id="email" name="email" type="text"/>

		<label for="message">${_(u'Messaggio')}: </label>
		<textarea id="message" name="message" cols="2" rows="2"></textarea>

		<div id="privacy_policy">
			<p>
				${h.literal(_(u"%s informa i visitatori del proprio sito di provvedere alla tutela dei dati personali nel rispetto ed in conformit&agrave; alle vigenti norme sulla privacy (Codice in materia di protezione dei dati personali - D.Lgs. n.196/2003)." % (c.settings['site_title'])))}
			</p>
			<p>
				${h.literal(_(u"Quando l'utente visita il sito, la sua presenza &egrave; anonima. Le informazioni personali, quali il nome o l'indirizzo e-mail, non vengono raccolte mentre si visita il medesimo."))}
			</p>
			<p>
				${h.literal(_(u"I dati personali dell'utente vengono dallo stesso forniti sul sito soltanto tramite la compilazione di form per l'accesso a servizi specifici."))}
			</p>
			<p>
				${h.literal(_(u"In tal caso i dati personali forniti sono raccolti e trattati in modo cartaceo ed elettronico solo nel caso in cui l'utente fornisca il proprio consenso ed al solo fine dell'erogazione del servizio in oggetto."))}
			</p>
			<p>
				${h.literal(_(u"All'interessato che fornisce i propri dati personali per le finalit&agrave; anzidette &egrave; assicurato il rispetto dei diritti riconosciutigli dall'art.7 del D.Lgs. n.196/2003."))}
			</p>
			<p>
				${h.literal(_(u"%s ha identificato il proprio responsabile del trattamento dei dati ai sensi dell'art.29 del citato Codice in materia di protezione dei dati personali (D.Lgs. n.196/2003)." % (c.settings['site_title'])))}
			</p>
		</div>

		<div class="agreement">
			<label for="agreement">${_(u'Accetto i termini di Privacy')}</label>
			<input id="agreement" name="agreement" type="checkbox" />
			<div class="reset">&nbsp;</div>
		</div>

		${h.captcha()}

		<input class="submit" id="submit" value="${_(u'Invia')}"
			title="${_(u'Invia il messaggio')}" type="submit" />

	</fieldset>
</form>
