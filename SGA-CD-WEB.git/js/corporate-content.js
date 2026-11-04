/* Published owner content, applied after the existing landing renders its sections. */
export async function applyCorporateContent(){
 const root=window.config.apiBaseUrl.replace(/\/$/,'');const response=await fetch(root+'/api/v1/workspace/corporate/sga-content',{cache:'no-store',silent:true});if(!response.ok)return;const settings=await response.json();
 if(settings.landing_seo_title)document.title=settings.landing_seo_title;
 if(settings.landing_seo_description){const meta=document.querySelector('meta[name=description]');if(meta)meta.content=settings.landing_seo_description;}
 if(settings.landing_footer_copy){const node=document.querySelector('#main-footer .footer-copy');if(node)node.textContent=settings.landing_footer_copy;}
 if(settings.landing_contact_email){const node=document.querySelector('#contact-info');if(node){let link=node.querySelector('a[href^="mailto:"]');if(!link){link=document.createElement('a');node.append(link);}link.href='mailto:'+settings.landing_contact_email;link.textContent=settings.landing_contact_email;}}
 for(const index of [1,2]){const row=document.querySelectorAll('#faq-container .faq-item')[index-1];if(!row)continue;const question=settings['landing_faq'+index+'_question'],answer=settings['landing_faq'+index+'_answer'];if(question){const node=row.querySelector('.faq-question span');if(node)node.textContent=question;}if(answer){const node=row.querySelector('.faq-answer p');if(node)node.textContent=answer;}}
 const url=settings.landing_logo_url;
 if(url&&(/^(https?:\/\/|assets\/)/.test(url))){const brand=document.querySelector('.sga-brand-logo');if(brand){const original=brand.querySelector('svg');let img=brand.querySelector('img[data-owner-logo]');if(!img){img=document.createElement('img');img.dataset.ownerLogo='true';img.alt='SGA-CD';img.width=42;img.height=42;img.style.objectFit='contain';img.addEventListener('error',()=>{img.remove();if(original)original.style.display='' });brand.prepend(img);}img.src=url;if(original)original.style.display='none';}}
}
